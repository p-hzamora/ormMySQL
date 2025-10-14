from __future__ import annotations

from ormlambda.sql.types import ColumnType, AliasType
from ..base import AbstractFunction


class Ceil(AbstractFunction):
    __visit_name__ = "ceil"

    def __init__[TProp](self, elements: ColumnType[TProp], alias: AliasType[ColumnType[TProp]] = "ceil"):
        super().__init__(elements, alias)

    @property
    def dtype(self) -> int:
        return int
