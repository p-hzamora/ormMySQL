from __future__ import annotations
from ormlambda.sql.functions.interface import IFunction

from ormlambda.sql.types import ColumnType

from ormlambda import Table

import typing as tp

from ormlambda.sql.elements import ClauseElement


if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.types import ColumnType, TableType


class Count[T: Table](ClauseElement, IFunction):
    __visit_name__ = "count"

    def __init__[TProp](
        self,
        element: str | ColumnType[TProp] | TableType[T] = "*",
        alias: str = "count",
    ) -> None:
        self.column = element
        self.alias = alias

    @property
    def dtype(self) -> str:
        return int

    def used_columns(self) -> tp.Iterable:
        if isinstance(self.column, str):
            # If is str, probably will by because we're using * so we don't have to retrieve something
            return []
        if not isinstance(self.column, tp.Iterable):
            return [self.column]
        return self.column


__all__ = ["Count"]
