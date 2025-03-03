from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType


class ST_AsText(AggregateFunctionBase[None]):
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
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            table=point.table,
            column=point,
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
        )
