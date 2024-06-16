from collections import defaultdict
from typing import Any, Callable, Literal, Optional

from ...interfaces.IQuery import IQuery


from .joins import JoinSelector, JoinType
from .select import SelectQuery
from .where_condition import WhereCondition
from .order import OrderQuery, OrderType
from ..table import Table
from ..foreign_key import ForeignKey

ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "with_recursive"]


class SQLQuery[T]:
    __order__: tuple[ORDER_QUERIES] = ("select", "join", "where", "order", "with", "with_recursive")

    def __init__(self) -> None:
        self._query: dict[ORDER_QUERIES, list[IQuery]] = defaultdict(list)

    def where(
        self,
        instance: tuple[Table],
        lambda_: Callable[[T], bool],
        **kwargs: dict[str, Any],
    ) -> WhereCondition:
        where_query = WhereCondition[T](function=lambda_, instances=instance, **kwargs)
        self._query["where"].append(where_query)
        return where_query

    def join(self, table_left: Table, table_right: Table, *, by: str) -> JoinSelector:
        where = ForeignKey.MAPPED[table_left.__table_name__][table_right.__table_name__]
        join_query = JoinSelector[table_left, Table](table_left, table_right, JoinType(by), where=where)
        self._query["join"].append(join_query)
        return join_query

    def select[*Ts](self, selector: Optional[Callable[[T, *Ts], None]] = lambda: None, *tables: tuple[T, *Ts]) -> SelectQuery:
        select = SelectQuery[T, *Ts](*tables, select_lambda=selector)
        self._query["select"].append(select)
        return select

    def order(self,instance:T, _lambda_col: Callable[[T], None], order_type: OrderType) -> OrderQuery:
        order = OrderQuery(instance, _lambda_col, order_type)
        self._query["order"].append(order)
        return order

    def build(self) -> str:
        query: str = ""
        self._create_necessary_inner_join()
        for x in self.__order__:
            if sub_query := self._query.get(x, None):
                if isinstance(sub_query[0], WhereCondition):
                    query_ = self.__build_where_clause(sub_query)
                else:
                    query_ = "\n".join([x.query for x in sub_query])

                query += f"\n{query_}"
        self._query.clear()
        return query

    def __build_where_clause(self, where_condition: list[WhereCondition]) -> str:
        query: str = where_condition[0].query

        for where in where_condition[1:]:
            q = where.query.replace(where.WHERE, "AND")
            and_, clause = q.split(" ", maxsplit=1)
            query += f" {and_} ({clause})"
        return query

    def _create_necessary_inner_join(self):
        select: SelectQuery = self._query["select"][0]
        tables: list[Table] = list(select.get_involved_tables().queue)

        # TODOM: updated lambda function in Where clausules to added tables
        # where: WhereCondition = self._query["where"][0]
        # tables_where: list[Table] = where.get_involved_tables()
        # avoid_repeated_table = set(tables).difference(set(tables_where))
        # tables.extend(list(avoid_repeated_table))

        if (n := len(tables)) > 1:
            for i in range(n - 1):
                l_tbl: Table = tables[i]
                r_tbl: Table = tables[i + 1]

                join = JoinSelector[l_tbl, r_tbl](l_tbl, r_tbl, JoinType.INNER_JOIN, where=ForeignKey.MAPPED[l_tbl.__table_name__][r_tbl.__table_name__])
                self._query["join"].append(join)

        pass
