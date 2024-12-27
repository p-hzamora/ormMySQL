from __future__ import annotations
from typing import override, Type, Callable, TYPE_CHECKING, Optional

from ormlambda.common.enums.join_type import JoinType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, ClauseInfoContext
from ormlambda.types import AliasType
from ormlambda.databases.my_sql.clauses.where import Where

if TYPE_CHECKING:
    from ormlambda import Table

from ormlambda.databases.my_sql.mysql_decomposition import MySQLDecompositionQuery


class Select[T: Type[Table], *Ts](MySQLDecompositionQuery[T, *Ts]):
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: Callable[[T], tuple] = lambda x: x,
        *,
        wheres: Optional[list[Where]] = None,
        by: JoinType = JoinType.INNER_JOIN,
        context: Optional[ClauseInfoContext] = None,
        alias_table: AliasType[ClauseInfo] = "{table}",
    ) -> None:
        context = context if context else ClauseInfoContext()
        super().__init__(
            tables,
            columns,
            by=by,
            context=context,
        )
        self._alias_table = alias_table
        self._wheres: list[Where] = [] if not wheres else wheres

    # TODOL: see who to deal when we will have to add more mysql methods
    @override
    @property
    def query(self) -> str:
        self.pop_tables_and_create_joins_from_ForeignKey()

        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'
        FROM = "FROM " + ClauseInfo[T](self.table, None, alias_table=self._alias_table, context=self._context).query
        JOINS = self.stringify_foreign_key(self._joins, " ")
        WHERE = Where.join_condition(self._wheres, True, self._context) if self._wheres else None
        COLUMNS = ClauseInfo.join_clauses(self._all_clauses, ",")
        SELECT = self.CLAUSE
        select_clauses = [
            SELECT,
            COLUMNS,
            FROM,
            JOINS,
            WHERE,
        ]

        return " ".join([x for x in select_clauses if x])
