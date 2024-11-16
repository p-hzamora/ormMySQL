from ormlambda.common.abstract_classes.clause_info import IAggregate, ClauseInfo


class ST_AsText(IAggregate):
    FUNCTION_NAME: str = "ST_AsText"

    def __init__[T, TProp](
        self,
        point_clause: ClauseInfo[TProp]
    ) -> None:
        self._point_column: ClauseInfo[TProp] = point_clause

    @property
    def query(self) -> str:
        return f"{self.FUNCTION_NAME}({self._point_column.query})"
