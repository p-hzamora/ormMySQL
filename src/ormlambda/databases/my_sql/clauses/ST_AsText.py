from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType


class ST_AsText[T, TProp](AggregateFunctionBase[None]):
    """
    https://dev.mysql.com/doc/refman/8.4/en/fetching-spatial-data.html

    The ST_AsText() function converts a geometry from internal format to a WKT string.
    """

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "ST_AsText"

    def __init__(
        self,
        point: ColumnType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = None,
        context: ClauseContextType = None,
    ) -> None:
        default_alias_clause = self.create_alias_from(point) if not alias_clause else alias_clause

        super().__init__(
            table=point.table,
            column=point,
            alias_table=alias_table,
            alias_clause=default_alias_clause,
            context=context,
        )

    @staticmethod
    def create_alias_from(element: ColumnType[TProp]) -> str:
        return element.column_name
