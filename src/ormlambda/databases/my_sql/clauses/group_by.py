from ormlambda.sql.clause_info import ClauseInfoContext
from ormlambda.sql.clauses import _GroupBy
from ormlambda.sql.types import ColumnType


class GroupBy(_GroupBy):
    def __init__(
        self,
        column: ColumnType,
        context: ClauseInfoContext,
        **kwargs,
    ):
        super().__init__(
            column=column,
            context=context,
            **kwargs,
        )
