from __future__ import annotations
from typing import Literal, override, Type, Callable, TYPE_CHECKING

from ormlambda.common.enums.join_type import JoinType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.types import AliasType
from ormlambda.databases.my_sql.clauses.where import Where
from ormlambda.common.interfaces.IQueryCommand import IQuery


if TYPE_CHECKING:
    from ormlambda import Table

from ormlambda.databases.my_sql.mysql_decomposition import MySQLDecompositionQuery

ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class Select[T: Type[Table], *Ts](MySQLDecompositionQuery[T, *Ts], IQuery):
    __order__: tuple[ORDER_QUERIES, ...] = ("join", "where", "order", "with", "group by", "limit", "offset")
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: Callable[[T], tuple] = lambda x: x,
        *,
        by: JoinType = JoinType.INNER_JOIN,
        alias_table: AliasType[ClauseInfo] = "{table}",
        **kwargs: list[IQuery],
    ) -> None:
        context = ClauseInfoContext()
        super().__init__(
            tables,
            columns,
            by=by,
            context=context,
        )
        self._alias_table = alias_table
        self._kwargs = kwargs

    # TODOL: see who to deal when we will have to add more mysql methods
    @override
    @property
    def query(self) -> str:
        joins = self.pop_tables_and_create_joins_from_ForeignKey()

        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'
        SELECT = self.CLAUSE
        FROM = "FROM " + ClauseInfo[T](self.table, None, alias_table=self._alias_table, context=self._context).query
        JOINS = self.stringify_foreign_key(joins, " ")
        WHERE = self._kwargs.get("where", [])
        ORDER = self._kwargs.get("order", None)
        GROUP_BY = self._kwargs.get("group_by", None)
        LIMIT = self._kwargs.get("limit", None)
        OFFSET = self._kwargs.get("offset", None)
        COLUMNS = ClauseInfo.join_clauses(self._all_clauses, ",")

        select_clauses = [
            SELECT,
            COLUMNS,
            FROM,
            JOINS,
            Where.join_condition(WHERE, True, self._context) if WHERE else None,
            " ".join(x.query for x in GROUP_BY) if GROUP_BY else None,
            " ".join(x.query for x in ORDER) if ORDER else None,
            " ".join(x.query for x in LIMIT) if LIMIT else None,
            " ".join(x.query for x in OFFSET) if OFFSET else None,
        ]

        return " ".join([x for x in select_clauses if x])

