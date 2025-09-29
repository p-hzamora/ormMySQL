from __future__ import annotations
from ormlambda import ColumnProxy
from ormlambda.sql.elements import ClauseElement
from typing import Any, Iterable, Optional, Type, TYPE_CHECKING

from ormlambda.sql.clause_info import ClauseInfo, IAggregate
from ormlambda.sql.types import SelectCol

if TYPE_CHECKING:
    from ormlambda.sql.types import AliasType, ColumnType
    from ormlambda.sql.table import TableProxy
    from ormlambda import Table

type Selectable = ColumnType | TableProxy


class Select[T: Type[Table]](ClauseElement, IAggregate):
    __visit_name__ = "select"

    def __init__(
        self,
        table: T,
        columns: SelectCol,
        *,
        alias_table: AliasType[ClauseInfo] = "{table}",
        alias: Optional[AliasType[T]] = None,
    ) -> None:
        self._table = table
        self._columns = columns
        self._alias_table = alias_table
        self._alias = alias

    @property
    def columns(self) -> tuple[SelectCol, ...]:
        if not isinstance(self._columns, Iterable):
            return [self._columns]
        return self._columns

    @property
    def table(self) -> Type[T]:
        return self._table

    @property
    def alias(self) -> str:
        return self._alias

    def used_columns(self):
        res = []

        for col in self._columns:
            if isinstance(col, ColumnProxy):
                res.append(col)

            elif isinstance(col, IAggregate):
                res.extend(col.used_columns())
        return res

    @property
    def dtype(self) -> Any: ...

    def __getitem__(self, key: str) -> SelectCol:
        for clause in self.columns:
            if isinstance(clause, ColumnProxy) and key in (clause.column_name, clause.alias, clause.get_full_chain("_")):
                return clause
            if isinstance(clause, IAggregate) and key == clause.alias:
                return clause


__all__ = ["Select"]
