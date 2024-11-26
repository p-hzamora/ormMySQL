from ormlambda.common.abstract_classes.clause_info import IAggregate, ClauseInfo


class ST_AsText(IAggregate):
    """
    https://dev.mysql.com/doc/refman/8.4/en/fetching-spatial-data.html
    
    The ST_AsText() function converts a geometry from internal format to a WKT string.
    """
    FUNCTION_NAME: str = "ST_AsText"

    def __init__[T, TProp](
        self,
        point_clause: ClauseInfo[TProp]
    ) -> None:
        self._point_column: ClauseInfo[TProp] = point_clause

    @property
    def query(self) -> str:
        return f"{self.FUNCTION_NAME}({self._point_column.query})"
