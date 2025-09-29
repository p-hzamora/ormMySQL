from __future__ import annotations
import typing as tp

from shapely import Point

from ormlambda import Column
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import IAggregate
from ormlambda.sql.elements import ClauseElement

class ST_Contains(ClauseElement, IAggregate):
    __visit_name__ = "st_contains"

    def __init__[TProp: Column](
        self,
        column: ColumnType[TProp],
        point: Point,
        alias: AliasType[ColumnType[TProp]]= "st_contains",
        
    ):
        self.column = column
        self.point = point
        self.alias = alias


    @property
    def dtype(self) -> str:
        return str

    def used_columns(self) -> tp.Iterable:
        return [self.attr1]
