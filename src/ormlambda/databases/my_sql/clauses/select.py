from __future__ import annotations
from typing import Optional, override, Type, Callable, TYPE_CHECKING

from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.sql.types import AliasType
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
from ormlambda.components import ISelect

if TYPE_CHECKING:
    from ormlambda import Table


class Select[T: Type[Table], *Ts](DecompositionQueryBase[T, *Ts], ISelect):
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: Callable[[T], tuple] = lambda x: x,
        *,
        alias_table: AliasType[ClauseInfo] = "{table}",
        context: Optional[ClauseInfoContext] = None,
    ) -> None:
        super().__init__(
            tables,
            columns,
            context=context,
        )
        self._alias_table = alias_table
        # We always need to add the self alias of the Select
        self._context._add_table_alias(self.table, self._alias_table)

    @property
    def FROM(self) -> ClauseInfo[T]:
        return ClauseInfo(self.table, None, alias_table=self._alias_table, context=self._context)

    @property
    def COLUMNS(self) -> str:
        return ClauseInfo.join_clauses(self._all_clauses, ",", self.context)

    # TODOL: see who to deal when we will have to add more mysql methods
    @override
    @property
    def query(self) -> str:
        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'
        FROM = self.FROM

        return f"{self.CLAUSE} {self.COLUMNS} FROM {FROM.query}"
