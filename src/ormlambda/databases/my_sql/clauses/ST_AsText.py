import typing as tp
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.types import ColumnType, AliasType
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


class ST_AsText(AggregateFunctionBase):
    """
    https://dev.mysql.com/doc/refman/8.4/en/fetching-spatial-data.html

    The ST_AsText() function converts a geometry from internal format to a WKT string.
    """

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "ST_AsText"

    def __init__[T, TProp](
        self,
        point: ColumnType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = None,
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        point_column: ClauseInfo[TProp] = ClauseInfo[T](point.table, point, alias_table=alias_table, context=context)
        super().__init__(
            column=point_column,
            alias_clause=alias_clause,
            context=None,
        )
