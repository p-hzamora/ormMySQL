from __future__ import annotations
import typing as tp

from ormlambda import Table, Column
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.clause_info import ClauseInfoContext, IAggregate

if tp.TYPE_CHECKING:
    from ormlambda.sql.types import ColumnType
    from ormlambda import Table
    from ormlambda.sql.types import AliasType


class Alias[T: Table, TProp](ClauseInfo, IQuery):
    def __init__(
        self,
        element: IAggregate | ClauseInfo[T] | ColumnType[TProp],
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]],
    ):
        if isinstance(element, Column):
            context = ClauseInfoContext()
            element = ClauseInfo(table=element.table, column=element, alias_clause=alias_clause)
        else:
            context = ClauseInfoContext(table_context=element.context._table_context, clause_context={})
            element.context = context
            element._alias_clause = alias_clause

        self._element = element

    @tp.override
    @property
    def query(self) -> str:
        return self._element.query
