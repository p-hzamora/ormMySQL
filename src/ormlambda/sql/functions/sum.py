from __future__ import annotations

from ormlambda.sql.elements import ClauseElement

from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import IAggregate


class Sum(ClauseElement, IAggregate):
    __visit_name__ = "sum"

    def __init__[TProp](
        self,
        elements: ColumnType[TProp],
        alias: AliasType[ColumnType[TProp]] = "sum",
    ):
        self.column = elements
        self.alias = alias

    def used_columns(self):
        return [self.column]

    @property
    def dtype(self) -> int:
        return int
