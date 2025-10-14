from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType

from ..base import AbstractFunction


class Truncate(AbstractFunction):
    __visit_name__ = "truncate"

    def __init__[TProp](self, elements: ColumnType[TProp], decimal: float, alias: AliasType[ColumnType[TProp]] = "truncate"):
        super().__init__(elements, alias)
        self._decimal = decimal

    @property
    def dtype(self) -> int:
        return int
