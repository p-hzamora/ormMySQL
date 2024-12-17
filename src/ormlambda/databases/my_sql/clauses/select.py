from __future__ import annotations
from typing import override, Type, Callable, TYPE_CHECKING, Optional

from ormlambda.common.enums.join_type import JoinType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, ClauseInfoContext
from ormlambda.types import AliasType

if TYPE_CHECKING:
    from ormlambda import Table
    from .joins import JoinSelector

from ..mysql_decomposition import MySQLDecompositionQuery


class Select[T: Type[Table], *Ts](MySQLDecompositionQuery[T, *Ts]):
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        lambda_query: Callable[[T], tuple] = lambda x: x,
        *,
        joins: Optional[list[JoinSelector]] = None,
        by: JoinType = JoinType.INNER_JOIN,
        context: Optional[ClauseInfoContext] = None,
        alias_table: AliasType[ClauseInfo] = "{table}",
    ) -> None:
        context = context if context else ClauseInfoContext()
        super().__init__(
            tables,
            lambda_query,
            by=by,
            joins=joins,
            context=context,
        )
        self._alias_table = alias_table

    # TODOL: see who to deal when we will have to add more mysql methods
    @override
    @property
    def query(self) -> str:
        # # FIXME [ ]: refactor ClauseInfo class
        # if isinstance(x, IAggregate) and x._row_column.has_foreign_keys:
        #     self._joins.update(x._row_column.fk_relationship)

        from_clause = "FROM " + ClauseInfo[T](self.table, None, alias_table=self._alias_table, context=self._context).query
        all_cols: str = ClauseInfo.join_clauses(self._all_clauses, ",")

        select_clauses = [
            self.CLAUSE,
            all_cols,
            from_clause,
        ]
        select_clause = " ".join(select_clauses)

        if self.has_foreign_keys:
            select_clause += " " + self.stringify_foreign_key(" ")

        return select_clause
