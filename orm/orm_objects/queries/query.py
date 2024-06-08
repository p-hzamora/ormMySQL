from collections import defaultdict
from queue import Queue
from typing import Callable, Literal, Optional


from .joins import JoinSelector, JoinType
from .select import SelectQuery
from .where_condition import WhereCondition
from .order import OrderQuery
from ..table import Table
from ..foreign_key import ForeignKey

ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "with_recursive"]


class SQLQuery[T]:
    __order__: tuple[ORDER_QUERIES] = ("select", "join", "where", "order", "with", "with_recursive")

    def __init__(self) -> None:
        self._query: dict[ORDER_QUERIES, list[str]] = defaultdict(list)

    def where(self, instance: T, lambda_function: Callable[[T], bool]) -> WhereCondition:
        where_query = WhereCondition[T, None](instance, None, lambda_function).to_query()
        self._query["where"].append(where_query)
        return where_query

    def join(self, table_left: Table, table_right: Table, *, by: str) -> JoinSelector:
        where = ForeignKey.MAPPED[table_left.__table_name__][table_right.__table_name__]
        join_query = JoinSelector[table_left, Table](table_left, table_right, JoinType(by), where=where).query
        self._query["join"].append(join_query)
        return join_query

    def select[*Ts](self, selector: Optional[Callable[[T, *Ts], None]] = lambda: None, *tables: tuple[T, *Ts]) -> SelectQuery:
        select = SelectQuery[T, *Ts](*tables, select_lambda=selector)
        self._query["select"].append(select.query)

        tables: Queue[Table] = select.get_involved_tables()

        if (n := tables.maxsize) > 1:
            for i in range(n - 1):
                l_tbl: Table = tables.queue[i]
                r_tbl: Table = tables.queue[i + 1]

                join = JoinSelector[l_tbl, r_tbl](l_tbl, r_tbl, JoinType.INNER_JOIN, where=ForeignKey.MAPPED[l_tbl.__table_name__][r_tbl.__table_name__])
                self._query["join"].append(join.query)

        return select

    def order(self, _lambda_col: Callable[[T], None], order_type: str) -> OrderQuery:
        order = OrderQuery(_lambda_col, order_type)
        self._query["order"].append(order.query)
        return order

    def build(self) -> str:
        query: str = ""
        for x in self.__order__:
            if sub_query := self._query.get(x, None):
                join_sub_query = "\n".join([x for x in sub_query])
                query += f"\n{join_sub_query}"
        self._query.clear()
        return query
