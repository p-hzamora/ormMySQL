from __future__ import annotations
from typing import Iterable, TypedDict, Optional

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql.clauses.joins import JoinSelector
from ormlambda import ForeignKey

from ormlambda.common.interfaces import IQuery


from ormlambda.sql.clause_info import ClauseInfo
from .clauses import Limit
from .clauses import Offset
from .clauses import Order
from .clauses import Select

from .clauses import Where
from .clauses import Having
from .clauses import GroupBy


from ormlambda.common.enums import JoinType


class OrderType(TypedDict):
    Select: Select
    JoinSelector: JoinSelector
    Where: Where
    Order: Order
    GroupBy: GroupBy
    Having: Having
    Limit: Limit
    Offset: Offset


class QueryBuilder(IQuery):
    __order__: tuple[str, ...] = ("Select", "JoinSelector", "Where", "GroupBy", "Having", "Order", "Limit", "Offset")

    def __init__(self, by: JoinType = JoinType.INNER_JOIN):
        self._context = ClauseInfoContext()
        self._query_list: OrderType = {}
        self._by = by

        self._joins: Optional[IQuery] = None
        self._select: Optional[IQuery] = None
        self._where: Optional[IQuery] = None
        self._order: Optional[IQuery] = None
        self._group_by: Optional[IQuery] = None
        self._limit: Optional[IQuery] = None
        self._offset: Optional[IQuery] = None

    def add_statement[T](self, clause: ClauseInfo[T]):
        self.update_context(clause)
        self._query_list[type(clause).__name__] = clause

    @property
    def by(self) -> JoinType:
        return self._by

    @by.setter
    def by(self, value: JoinType) -> None:
        self._by = value

    @property
    def JOINS(self) -> Optional[set[JoinSelector]]:
        return self._joins

    @property
    def SELECT(self) -> IQuery:
        return self._query_list.get("Select", None)

    @property
    def WHERE(self) -> IQuery:
        where = self._query_list.get("Where", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def ORDER(self) -> IQuery:
        return self._query_list.get("Order", None)

    @property
    def GROUP_BY(self) -> IQuery:
        return self._query_list.get("GroupBy", None)

    @property
    def HAVING(self) -> IQuery:
        where = self._query_list.get("Having", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def LIMIT(self) -> IQuery:
        return self._query_list.get("Limit", None)

    @property
    def OFFSET(self) -> IQuery:
        return self._query_list.get("Offset", None)

    @property
    def query(self) -> str:
        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'

        extract_joins = self.pop_tables_and_create_joins_from_ForeignKey(self._by)

        JOINS = self.stringify_foreign_key(extract_joins, " ")
        query_list: tuple[str, ...] = (
            self.SELECT.query,
            JOINS,
            Where.join_condition(self.WHERE, True, self._context) if self.WHERE else None,
            self.GROUP_BY.query if self.GROUP_BY else None,
            Having.join_condition(self.HAVING, True, self._context) if self.HAVING else None,
            self.ORDER.query if self.ORDER else None,
            self.LIMIT.query if self.LIMIT else None,
            self.OFFSET.query if self.OFFSET else None,
        )
        return " ".join([x for x in query_list if x])

    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> Optional[str]:
        if not joins:
            return None
        sorted_joins = JoinSelector.sort_join_selectors(joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def pop_tables_and_create_joins_from_ForeignKey(self, by: JoinType = JoinType.INNER_JOIN) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        joins = set()
        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for fk in ForeignKey.stored_calls.copy():
            fk = ForeignKey.stored_calls.pop(fk)
            self._context._add_table_alias(fk.tright, fk.alias)
            join = JoinSelector(fk.resolved_function(self._context), by, context=self._context, alias=fk.alias)
            joins.add(join)

        return joins

    def clear(self) -> None:
        self.__init__()
        return None

    def update_context(self, clause: ClauseInfo) -> None:
        if not hasattr(clause, "context"):
            return None

        if clause.context is not None:
            self._context.update(clause.context)
        clause.context = self._context
