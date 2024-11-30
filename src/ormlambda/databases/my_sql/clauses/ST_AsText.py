import typing as tp
from ormlambda.common.abstract_classes.clause_info import IAggregate, ClauseInfo
from ormlambda.types import ColumnType, AliasType


class ST_AsText(IAggregate):
    """
    https://dev.mysql.com/doc/refman/8.4/en/fetching-spatial-data.html

    The ST_AsText() function converts a geometry from internal format to a WKT string.
    """

    FUNCTION_NAME: str = "ST_AsText"

    def __init__[T, TProp](
        self,
        point: ColumnType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = None,
    ) -> None:
        self._point_column: ClauseInfo[TProp] = ClauseInfo[T](point.table, point, alias_table)
        self._alias_clause: AliasType[ColumnType[TProp]] = alias_clause

    @property
    def query(self) -> str:
        return f"{self.FUNCTION_NAME}({self._point_column.query})"

    @property
    def alias_clause(self) -> tp.Optional[str]:
        return self._alias_clause
