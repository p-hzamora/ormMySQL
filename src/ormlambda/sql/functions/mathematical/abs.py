from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Abs(AbstractFunction):
    __visit_name__ = "abs"

    def __init__[TProp](self, elements: ColumnType[TProp], alias: AliasType[ColumnType[TProp]] = "abs"):
        super().__init__(elements, alias)

    @property
    def dtype(self) -> int:
        return int
