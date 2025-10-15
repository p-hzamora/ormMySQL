from __future__ import annotations
from ormlambda.sql.functions.interface import IFunction
from ormlambda.sql.types import ColumnType, AliasType

from ormlambda.sql.elements import ClauseElement


class ST_AsText[T, TProp](ClauseElement, IFunction):
    """
    https://dev.mysql.com/doc/refman/8.4/en/fetching-spatial-data.html

    The ST_AsText() function converts a geometry from internal format to a WKT string.
    """

    __visit_name__ = "st_astext"

    def __init__(self, point: ColumnType[TProp], alias: AliasType[TProp] = "st_astext") -> None:
        self.alias = alias
        self.column = point

    def used_columns(self):
        return [self.column]

    @property
    def dtype(self) -> str:
        return str
