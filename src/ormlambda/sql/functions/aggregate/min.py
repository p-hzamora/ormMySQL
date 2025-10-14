from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Min(AbstractFunction):
    __visit_name__ = "min"

    def __init__[TProp](self, elements: ColumnType[TProp], alias: AliasType[ColumnType[TProp]] = "min"):
        super().__init__(elements, alias)

    @property
    def dtype(self) -> int:
        return int
