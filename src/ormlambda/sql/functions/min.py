from __future__ import annotations

from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import IAggregate


class Min(ClauseElement, IAggregate):
    __visit_name__ = "min"

    def __init__[TProp](
        self,
        elements: ColumnType[TProp],
        alias: AliasType[ColumnType[TProp]] = "min",
    ):
        self.column = elements
        self.alias = alias

    def used_columns(self):
        return [self.column]

    @property
    def dtype(self) -> int:
        return int
