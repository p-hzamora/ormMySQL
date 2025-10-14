from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Pow(AbstractFunction):
    __visit_name__ = "pow"

    def __init__[TProp](self, elements: ColumnType[TProp], exponent: float, alias: AliasType[ColumnType[TProp]] = "pow"):
        super().__init__(elements, alias)
        self._exponent = exponent

    @property
    def dtype(self) -> int:
        return int
