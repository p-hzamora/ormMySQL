from __future__ import annotations
from typing import Type, TYPE_CHECKING, Optional, Callable

from ormlambda.sql.clauses import _Select

from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.sql.types import AliasType

if TYPE_CHECKING:
    from ormlambda import Table


class Select[T: Type[Table], *Ts](_Select[T, *Ts]):
    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: Callable[[T], tuple] = lambda x: x,
        *,
        alias_table: AliasType[ClauseInfo] = "{table}",
        context: Optional[ClauseInfoContext] = None,
        **kwargs,
    ):
        super().__init__(
            tables,
            columns,
            alias_table=alias_table,
            context=context,
            **kwargs,
        )
