from __future__ import annotations
from typing import Iterable, TypedDict, Optional, TYPE_CHECKING

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.sql.clauses import JoinSelector
from ormlambda import ForeignKey

from ormlambda.common.interfaces import IQuery


from ormlambda.sql.clause_info import ClauseInfo

if TYPE_CHECKING:
    from ..sql.clauses import Limit as Limit
    from ..sql.clauses import Offset as Offset
    from ..sql.clauses import Order as Order
    from ..sql.clauses import Select as Select

    from ..sql.clauses import GroupBy as GroupBy

    from ormlambda.dialects import Dialect

from ..sql.clauses import Where as Where
from ..sql.clauses import Having as Having
from ormlambda.common.enums import JoinType
from ormlambda.sql.elements import ClauseElement


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

    def __init__(self, dialect: Dialect, by: JoinType = JoinType.INNER_JOIN):
        self.dialect = dialect
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
    def SELECT(self) -> ClauseElement:
        return self._query_list.get("Select", None)

    @property
    def WHERE(self) -> ClauseElement:
        where = self._query_list.get("Where", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def ORDER(self) -> ClauseElement:
        return self._query_list.get("Order", None)

    @property
    def GROUP_BY(self) -> ClauseElement:
        return self._query_list.get("GroupBy", None)

    @property
    def HAVING(self) -> ClauseElement:
        where = self._query_list.get("Having", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def LIMIT(self) -> ClauseElement:
        return self._query_list.get("Limit", None)

    @property
    def OFFSET(self) -> ClauseElement:
        return self._query_list.get("Offset", None)

    def query(self, dialect: Dialect, **kwargs) -> str:
        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'

        extract_joins = self.pop_tables_and_create_joins_from_ForeignKey(self._by)

        JOINS = self.stringify_foreign_key(extract_joins, " ")
        query_list: tuple[str, ...] = (
            self.SELECT.compile(dialect).string,
            JOINS,
            Where.join_condition(self.WHERE, True, self._context, dialect=dialect) if self.WHERE else None,
            self.GROUP_BY.compile(dialect).string if self.GROUP_BY else None,
            Having.join_condition(self.HAVING, True, self._context, dialect=dialect) if self.HAVING else None,
            self.ORDER.compile(dialect).string if self.ORDER else None,
            self.LIMIT.compile(dialect).string if self.LIMIT else None,
            self.OFFSET.compile(dialect).string if self.OFFSET else None,
        )
        return " ".join([x for x in query_list if x])

    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> Optional[str]:
        if not joins:
            return None
        sorted_joins = JoinSelector.sort_join_selectors(joins)
        return f"{sep}".join([join.query(self.dialect) for join in sorted_joins])

    def pop_tables_and_create_joins_from_ForeignKey(self, by: JoinType = JoinType.INNER_JOIN) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        joins = set()
        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for fk in ForeignKey.stored_calls.copy():
            fk = ForeignKey.stored_calls.pop(fk)
            fk_alias = fk.get_alias(self.dialect)
            self._context._add_table_alias(fk.tright, fk_alias)
            join = JoinSelector(fk.resolved_function(self._context), by, context=self._context, alias=fk_alias, dialect=self.dialect)
            joins.add(join)

        return joins

    def clear(self) -> None:
        self.__init__(self.dialect, self.by)
        return None

    def update_context(self, clause: ClauseInfo) -> None:
        if not hasattr(clause, "context"):
            return None

        if clause.context is not None:
            self._context.update(clause.context)
        clause.context = self._context
