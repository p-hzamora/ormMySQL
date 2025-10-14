from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Mod(AbstractFunction):
    __visit_name__ = "mod"

    def __init__[TProp](self, elements: ColumnType[TProp], divisor: float, alias: AliasType[ColumnType[TProp]] = "mod"):
        super().__init__(elements, alias)
        self._divisor = divisor

    @property
    def dtype(self) -> int:
        return int
