import typing as tp

from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo

from ormlambda.types import ColumnType
from ormlambda import Column
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase

if tp.TYPE_CHECKING:
    from ormlambda import Table


class AbstractAggregateFunction[T: tp.Type[Table]](AggregateFunctionBase):
    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp]] | ColumnType[TProp],
        alias_name: str = ...,
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        if not isinstance(column, tp.Iterable):
            column = (column,)

        all_clauses: list[ClauseInfo] = []
        for col in column:
            table: tp.Optional[Table] = col.table if isinstance(col, Column) else None
            all_clauses.append(ClauseInfo(table, col, context=context))

        column = ClauseInfo.join_clauses(all_clauses)
        super().__init__(column=column, alias_clause=alias_name, context=context)
