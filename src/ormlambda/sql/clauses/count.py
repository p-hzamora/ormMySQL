from __future__ import annotations
from ormlambda.sql.clause_info import IAggregate

from ormlambda.sql.types import ColumnType

from ormlambda import Table

import typing as tp

from ormlambda.sql.elements import ClauseElement


if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.types import ColumnType, TableType


class Count[T: Table](ClauseElement, IAggregate):
    __visit_name__ = "count"

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "COUNT"

    def __init__[TProp: Table](
        self,
        element: ColumnType[T] | TableType[TProp] = "*",
        alias: str = "count",
    ) -> None:
        self.column = element
        self.alias = alias

    @property
    def dtype(self) -> str:
        return int


__all__ = ["Count"]
