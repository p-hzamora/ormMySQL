from __future__ import annotations
import typing as tp
import abc
from ormlambda import Table, Column

from ormlambda.common.interfaces import IDecompositionQuery, ICustomAlias
from ormlambda.sql.clause_info import IAggregate
from ormlambda.sql.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda import ForeignKey
from ormlambda.common.global_checker import GlobalChecker

from ormlambda.sql.types import AliasType, TableType, ColumnType


type TableTupleType[T, *Ts] = tuple[T:TableType, *Ts]
type ValueType = tp.Union[
    tp.Type[IAggregate],
    tp.Type[Table],
    tp.Type[str],
    tp.Type[ICustomAlias],
]


class ClauseInfoConverter[T, TProp](abc.ABC):
    @classmethod
    @abc.abstractmethod
    def convert(cls, data: T, alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None) -> list[ClauseInfo[T]]: ...


class ConvertFromAnyType(ClauseInfoConverter[None, None]):
    @classmethod
    def convert(cls, data: tp.Any, alias_table: AliasType = "{table}", context: ClauseContextType = None) -> list[ClauseInfo[None]]:
        return [
            ClauseInfo[None](
                table=None,
                column=data,
                alias_table=alias_table,
                alias_clause=None,
                context=context,
            )
        ]


class ConvertFromForeignKey[LT: Table, RT: Table](ClauseInfoConverter[RT, None]):
    @classmethod
    def convert(cls, data: ForeignKey[LT, RT], alias_table=None, context: ClauseContextType = None) -> list[ClauseInfo[RT]]:
        return ConvertFromTable[RT].convert(data.tright, data.alias, context)


class ConvertFromColumn[TProp](ClauseInfoConverter[None, TProp]):
    @classmethod
    def convert(cls, data: ColumnType[TProp], alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None) -> list[ClauseInfo[None]]:
        # COMMENT: if the property belongs to the main class, the columnn name in not prefixed. This only done if the property comes from any join.
        clause_info = ClauseInfo[None](
            table=data.table,
            column=data,
            alias_table=alias_table,
            alias_clause="{table}_{column}",
            context=context,
        )
        return [clause_info]


class ConvertFromIAggregate(ClauseInfoConverter[None, None]):
    @classmethod
    def convert(cls, data: AggregateFunctionBase, alias_table=None, context: ClauseContextType = None) -> list[ClauseInfo[None]]:
        return [data]


class ConvertFromTable[T: Table](ClauseInfoConverter[T, None]):
    @classmethod
    def convert(cls, data: T, alias_table: AliasType[ColumnType] = "{table}", context: ClauseContextType = None) -> list[ClauseInfo[T]]:
        """
        if the data is Table, means that we want to retrieve all columns
        """
        return cls._extract_all_clauses(data, alias_table, context)

    @staticmethod
    def _extract_all_clauses(table: TableType[T], alias_table: AliasType[ColumnType], context: ClauseContextType = None) -> list[ClauseInfo[TableType[T]]]:
        # all columns
        column_clauses = []
        for column in table.get_columns():
            column_clauses.extend(ConvertFromColumn.convert(column, alias_table=alias_table, context=context))
        return column_clauses


class DecompositionQueryBase[T: Table, *Ts](IDecompositionQuery[T, *Ts]):
    @tp.overload
    def __init__(self, tables: tuple[TableType[T]], columns: tuple[ColumnType]) -> None: ...
    @tp.overload
    def __init__(self, tables: tuple[TableType[T]], columns: tuple[ColumnType], context: ClauseContextType = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: tuple[TableType[T]], columns: tuple[ColumnType], alias_table: str, context: ClauseContextType = ...) -> None: ...

    def __init__(self, tables: tuple[TableType[T]], columns: tuple[ColumnType], alias_table: str = "{table}", *, context: ClauseContextType = ClauseInfoContext()) -> None:
        self._tables: tuple[TableType[T]] = tables if isinstance(tables, tp.Iterable) else (tables,)

        self._columns: tp.Callable[[T], tuple] = columns
        self._all_clauses: list[ClauseInfo | AggregateFunctionBase] = []
        self._context: ClauseContextType = context if context else ClauseInfoContext()
        self._alias_table: str = alias_table
        self.__clauses_list_generetor()

    def __getitem__(self, key: str) -> ClauseInfo | AggregateFunctionBase:
        for clause in self._all_clauses:
            is_agg_function = isinstance(clause, AggregateFunctionBase)
            is_clause_info = isinstance(clause, ClauseInfo)
            if (is_agg_function and clause._alias_aggregate == key) or (is_clause_info and clause.alias_clause == key):
                return clause

    def __clauses_list_generetor(self) -> None:
        # Clean self._all_clauses if we update the context
        self._all_clauses.clear() if self._all_clauses else None

        resolved_function = GlobalChecker.resolved_callback_object(self._columns, self.tables)

        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (self.table,) if ClauseInfo.is_asterisk(resolved_function) else (resolved_function,)

        for data in resolved_function:
            if not isinstance(data, ClauseInfo):
                values = self.__convert_into_ClauseInfo(data)
            else:
                values = [data]
            self.__add_clause(values)

        return None

    def __convert_into_ClauseInfo[TProp](self, data: TProp) -> list[ClauseInfo[T]]:
        """
        A method that behaves based on the variable's type
        """

        def validation(data: TProp, type_: ValueType) -> bool:
            is_valid_type: bool = isinstance(data, type) and issubclass(data, type_)
            return isinstance(data, type_) or is_valid_type

        VALUE_TYPE_MAPPED: dict[tp.Type[ValueType], ClauseInfoConverter[T, TProp]] = {
            ForeignKey: ConvertFromForeignKey[T, Table],
            Column: ConvertFromColumn[TProp],
            IAggregate: ConvertFromIAggregate,
            Table: ConvertFromTable[T],
        }
        classConverter = next((converter for obj, converter in VALUE_TYPE_MAPPED.items() if validation(data, obj)), ConvertFromAnyType)

        return classConverter.convert(data, alias_table=self._alias_table, context=self._context)

    def __add_clause[TTable: TableType](self, clauses: list[ClauseInfo[TTable]] | ClauseInfo[TTable]) -> None:
        if not isinstance(clauses, tp.Iterable):
            raise ValueError(f"Iterable expected. '{type(clauses)}' got instead.")

        for clause in clauses:
            self._all_clauses.append(clause)
        return None

    @property
    def table(self) -> T:
        return self.tables[0] if isinstance(self.tables, tp.Iterable) else self.tables

    @property
    def tables(self) -> T:
        return self._tables

    @property
    def columns[*Ts](self) -> tp.Callable[[T], tuple[*Ts]]:
        return self._columns

    @property
    def all_clauses(self) -> list[ClauseInfo[T]]:
        return self._all_clauses

    @property
    def context(self) -> tp.Optional[ClauseInfoContext]:
        return self._context

    @context.setter
    def context(self, value: ClauseInfoContext) -> None:
        self._context = value
        self.__clauses_list_generetor()
        return None
