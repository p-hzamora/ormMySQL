from __future__ import annotations
from collections import defaultdict
import typing as tp
import abc
from ormlambda import Table, Column

from ormlambda.common.interfaces import IAggregate, IDecompositionQuery, ICustomAlias
from ormlambda import JoinType
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.utils.foreign_key import ForeignKey
from ormlambda.utils.global_checker import GlobalChecker

from ormlambda.types import AliasType, TableType, ColumnType
from ormlambda.common.errors import UnmatchedLambdaParameterError

if tp.TYPE_CHECKING:
    from ormlambda.databases.my_sql.clauses.joins import JoinSelector


type TableTupleType[T, *Ts] = tuple[T:TableType, *Ts]
type ValueType = tp.Union[
    IAggregate,
    Table,
    str,
    ICustomAlias,
]


class ClauseInfoConverter[T, TProp](abc.ABC):
    @classmethod
    @abc.abstractmethod
    def convert(cls, data: T, alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None) -> list[ClauseInfo[T]]: ...


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
    def __init__(self, tables: TableTupleType, columns: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, columns: tp.Callable[[T], tuple], *, by: JoinType = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, columns: tp.Callable[[T], tuple], *, by: JoinType = ..., joins: tp.Optional[set[IJoinSelector]] = ...) -> None: ...

    def __init__(self, tables: TableTupleType, columns: tp.Callable[[T], tuple[*Ts]], *, by: JoinType = JoinType.INNER_JOIN, joins: tp.Optional[set[IJoinSelector]] = None, context: ClauseContextType = None) -> None:
        self._tables: TableTupleType = tables if isinstance(tables, tp.Iterable) else (tables,)

        self._columns: tp.Callable[[T], tuple] = columns
        self._by: JoinType = by
        self._joins: set[IJoinSelector] = set()
        self._clauses_group_by_tables: dict[TableType, list[ClauseInfo[T]]] = defaultdict(list)
        self._all_clauses: list[ClauseInfo] = []
        self._alias_cache: dict[str, AliasType] = {}
        self._context: ClauseContextType = context if context else ClauseInfoContext()

        self.__clauses_list_generetor()

    def __getitem__(self, key: str) -> ClauseInfo:
        for clause in self._all_clauses:
            if clause.alias_clause == key:
                return clause

    def __clauses_list_generetor(self) -> None:
        if not GlobalChecker.is_lambda_function(self._columns):
            resolved_function = self._columns
        else:
            try:
                resolved_function = self._columns(*self.tables)
            except TypeError:
                raise UnmatchedLambdaParameterError(len(self.tables), self._columns)

        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (self.table,) if ClauseInfo.is_asterisk(resolved_function) else (resolved_function,)

        for data in resolved_function:
            values = self.__convert_into_ClauseInfo(data)
            self.__add_clause(values)

        return None

    def __convert_into_ClauseInfo[TProp](self, data: TProp) -> list[ClauseInfo[T]]:
        """
        A method that behaves based on the variable's type
        """

        def validation(data: TProp, type_: ValueType) -> bool:
            is_table: bool = isinstance(data, type) and issubclass(data, type_)
            return any(
                [
                    isinstance(data, type_),
                    is_table,
                ]
            )

        value_type_mapped: dict[tp.Type[ValueType], ClauseInfoConverter[T, TProp]] = {
            ForeignKey: ConvertFromForeignKey[T, Table],
            Column: ConvertFromColumn[TProp],
            IAggregate: ConvertFromIAggregate,
            Table: ConvertFromTable[T],
        }
        classConverter = next((handler for cls, handler in value_type_mapped.items() if validation(data, cls)), None)

        if not classConverter:
            raise NotImplementedError(f"type of value '{data}' is not implemented.")

        return classConverter.convert(data, context=self._context)

    def __add_clause[TTable: TableType](self, clauses: list[ClauseInfo[TTable]] | ClauseInfo[TTable]) -> None:
        if not isinstance(clauses, tp.Iterable):
            raise ValueError(f"Iterable expected. '{type(clauses)}' got instead.")

        for clause in clauses:
            self._all_clauses.append(clause)
            self._clauses_group_by_tables[clause.table].append(clause)
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
    def clauses_group_by_tables(self) -> dict[TableType, list[ClauseInfo[T]]]:
        return self._clauses_group_by_tables

    @property
    @abc.abstractmethod
    def query(self) -> str: ...

    @abc.abstractmethod
    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> str: ...

    def pop_tables_and_create_joins_from_ForeignKey(self) -> None:
        from ormlambda.databases.my_sql.clauses.joins import JoinSelector

        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for _ in range(len(ForeignKey.stored_calls)):
            fk = ForeignKey.stored_calls.pop()
            join = JoinSelector(fk.resolved_function(lambda: self._context), self._by, context=self._context, alias=fk.alias)
            self._joins.add(join)
            self._context._add_table_alias(join.right_table, join.alias)

        return None
