from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Sqrt(AbstractFunction):
    __visit_name__ = "sqrt"

    def __init__[TProp](self, elements: ColumnType[TProp], alias: AliasType[ColumnType[TProp]] = "sqrt"):
        super().__init__(elements, alias)

    @property
    def dtype(self) -> int:
        return int
