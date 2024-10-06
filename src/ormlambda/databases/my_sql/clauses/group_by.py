from typing import Callable
from ormlambda.common.enums.join_type import JoinType
from .select import SelectQuery
from ormlambda import Table


class GroupBy[T: Table, TProp, *Ts](SelectQuery[T, *Ts]):
    def __init__(
        self,
        tables: T | tuple[T, *Ts],
        column: TProp,
        select_lambda: Callable[[T], tuple[*Ts]],
        *,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(tables, select_lambda, by=by)
        self._column: TProp = column
