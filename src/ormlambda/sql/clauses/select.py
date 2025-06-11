from __future__ import annotations
from ormlambda.sql.elements import ClauseElement
from typing import Optional, Type, Callable, TYPE_CHECKING

from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.sql.types import AliasType
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.dialects import Dialect


class Select[T: Type[Table], *Ts](DecompositionQueryBase[T, *Ts], ClauseElement):
    __visit_name__ = "select"

    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: Callable[[T], tuple] = lambda x: x,
        *,
        alias_table: AliasType[ClauseInfo] = "{table}",
        context: Optional[ClauseInfoContext] = None,
        dialect: Dialect,
        **kwargs,
    ) -> None:
        super().__init__(
            tables,
            columns,
            context=context,
            dialect=dialect,
            **kwargs,
        )
        self._alias_table = alias_table
        # We always need to add the self alias of the Select
        self._context._add_table_alias(self.table, self._alias_table)

    @property
    def FROM(self) -> ClauseInfo[T]:
        return ClauseInfo(self.table, None, alias_table=self._alias_table, context=self._context, dialect=self._dialect, **self.kwargs)

    @property
    def COLUMNS(self) -> str:
        dialect = self.kwargs.pop("dialect", self._dialect)
        return ClauseInfo.join_clauses(self._all_clauses, ",", self.context, dialect=dialect)


__all__ = ["Select"]
