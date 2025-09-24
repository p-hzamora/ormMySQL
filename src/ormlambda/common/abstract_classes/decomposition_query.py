from __future__ import annotations
from typing import Union,Type, TYPE_CHECKING,Iterable,overload
from ormlambda import Table, Column, ColumnProxy, TableProxy

from ormlambda.common.interfaces import IDecompositionQuery, ICustomAlias
from ormlambda.sql.clause_info import IAggregate
from ormlambda.sql.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda import ForeignKey


from ormlambda.sql.types import TableType, ColumnType
from .clause_info_converter import (
    ClauseInfoConverter,
    ConvertFromAnyType,
    ConvertFromForeignKey,
    ConvertFromColumn,
    ConvertFromColumnProxy,
    ConvertFromIAggregate,
    ConvertFromTable,
    ConvertFromTableProxy,
)

type TableTupleType[T, *Ts] = tuple[T:TableType, *Ts]
type ValueType = Union[
    Type[IAggregate],
    Type[Table],
    Type[str],
    Type[ICustomAlias],
]

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
    from ormlambda import Alias


class DecompositionQueryBase[T: Table, *Ts](IDecompositionQuery[T, *Ts]):
    @overload
    def __init__(self, tables: tuple[TableType[T]], columns: tuple[ColumnType]) -> None: ...

    def __init__(
        self,
        tables: tuple[TableType[T]],
        columns: tuple[ColumnType, ...],
        alias_table: str = "{table}",
        *,
        dialect: Dialect,
        **kwargs,
    ) -> None:
        self.kwargs = kwargs
        self._tables: tuple[TableType[T]] = tables if isinstance(tables, Iterable) else (tables,)

        self._dialect = dialect
        self._columns: Iterable[ColumnType] = columns
        self._all_clauses: list[ClauseInfo | AggregateFunctionBase] = []
        self._alias_table: str = alias_table

    def __getitem__(self, key: str) -> ClauseInfo | AggregateFunctionBase:
        for clause in self.columns:
            if isinstance(clause, ColumnProxy) and key in (clause.column_name, clause.alias):
                return self.__convert_into_ClauseInfo(clause)[0]
            if isinstance(clause, IAggregate) and key == clause.alias:
                return self.__convert_into_ClauseInfo(clause)[0]

    def __clauses_list_generetor(self) -> None:
        # Clean self._all_clauses if we update the context
        self._all_clauses.clear() if self._all_clauses else None

        resolved_function = self._columns

        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, Iterable):
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

        VALUE_TYPE_MAPPED: dict[Type[ValueType], ClauseInfoConverter[T, TProp]] = {
            ForeignKey: ConvertFromForeignKey[T, Table],
            ColumnProxy: ConvertFromColumnProxy[TProp],
            Column: ConvertFromColumn[TProp],
            IAggregate: ConvertFromIAggregate,
            TableProxy: ConvertFromTableProxy[T],
            Table: ConvertFromTable[T],
        }
        classConverter = next((converter for obj, converter in VALUE_TYPE_MAPPED.items() if validation(data, obj)), ConvertFromAnyType)
        self.kwargs.setdefault("dialect", self._dialect)
        if "dialect" not in self.kwargs:
            raise ValueError("You must specified 'dialect' variable")
        return classConverter.convert(data, alias_table=self._alias_table, **self.kwargs)

    def __add_clause[TTable: TableType](self, clauses: list[ClauseInfo[TTable]] | ClauseInfo[TTable]) -> None:
        if not isinstance(clauses, Iterable):
            raise ValueError(f"Iterable expected. '{type(clauses)}' got instead.")

        for clause in clauses:
            self._all_clauses.append(clause)
        return None

    @property
    def table(self) -> T:
        return self.tables[0] if isinstance(self.tables, Iterable) else self.tables

    @property
    def tables(self) -> T:
        return self._tables

    @property
    def columns[*Ts](self) -> Iterable[ColumnProxy | Alias]:
        return self._columns

    @property
    def all_clauses(self) -> list[ClauseInfo[T] | IAggregate]:
        if not self._all_clauses:
            self.__clauses_list_generetor()

        return self._all_clauses
