from __future__ import annotations
from ormlambda.common.abstract_classes.clause_info import ClauseInfo

from ormlambda.utils.table_constructor import Table

import typing as tp

from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


if tp.TYPE_CHECKING:
    from ormlambda.common.interfaces.IAggregate import IAggregate
    from ormlambda import Table
    from ormlambda.types import AliasType


class Alias[T: Table](IQuery):
    def __init__(
        self,
        element: IAggregate | ClauseInfo[T],
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]],
    ):
        context = ClauseInfoContext(table_context=element.context._table_context, clause_context={})
        element.context = context
        self._element = element
        self._element._alias_clause = alias_clause

    @tp.override
    @property
    def query(self) -> str:
        return self._element.query
