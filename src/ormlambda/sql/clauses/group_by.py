from __future__ import annotations
from typing import Any, Iterable

from ormlambda.sql.functions.interface import IFunction

from ormlambda.sql.types import ColumnType
from ormlambda.sql.elements import ClauseElement


class GroupBy(ClauseElement, IFunction):
    __visit_name__ = "group_by"

    def __init__(self, *column: ColumnType):
        self.column: tuple[ColumnType] = column if isinstance(column, Iterable) else [column]

    def used_columns(self):
        return self.column

    @property
    def dtype(self) -> Any:
        return ...


__all__ = ["GroupBy"]
