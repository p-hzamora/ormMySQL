from __future__ import annotations
import typing as tp

from shapely import Point

from ormlambda import Column
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import ClauseInfo, IAggregate

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class ST_Contains(IAggregate):
    FUNCTION_NAME: str = "ST_Contains"

    def __init__[TProp: Column](
        self,
        column: ColumnType[TProp],
        point: Point,
        alias_table: tp.Optional[AliasType[ColumnType[TProp]]] = None,
        alias_clause: tp.Optional[AliasType[ColumnType[TProp]]] = None,
        *,
        dialect: Dialect,
    ):
        self.attr1: ClauseInfo[Point] = ClauseInfo(column.table, column, alias_table, dialect=dialect)
        self.attr2: ClauseInfo[Point] = ClauseInfo[Point](None, point, dialect=dialect)

        self._alias_clause: AliasType[ColumnType[TProp]] = alias_clause

    def query(self, dialect: Dialect, **kwargs) -> str:
        return f"{self.FUNCTION_NAME}({self.attr1.query(dialect,**kwargs)}, {self.attr2.query(dialect,**kwargs)})"

    @property
    def alias_clause(self) -> tp.Optional[str]:
        return self._alias_clause
