import typing as tp
from ormlambda import Table
from ormlambda.sql.clause_info import ClauseInfoContext
from ormlambda.sql.clauses import _GroupBy
from ormlambda.sql.types import ColumnType


class GroupBy[T: tp.Type[Table], *Ts, TProp](_GroupBy[T, *Ts, TProp]):
    def __init__(
        self,
        column: ColumnType,
        context: ClauseInfoContext,
        **kwargs,
    ):
        super().__init__(column=column, context=context, **kwargs,)
