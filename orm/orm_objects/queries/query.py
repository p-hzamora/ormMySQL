from collections import defaultdict
from typing import Callable, Literal, Iterable, Optional

from orm.orm_objects.table import Table
from .where_condition import WhereCondition

OrderQuery = Literal["select", "join", "where", "order", "with", "with_recursive"]


class SQLQuery[T]:
    __order__: tuple[OrderQuery] = ("select", "join", "where", "order", "with", "with_recursive")

    def __init__[T2](self) -> None:
        self._query: dict[OrderQuery, list[str]] = defaultdict(list)


    def order(self, _lambda_col: Callable[[T], None], order_type: str) -> OrderQuery:
        order = OrderQuery(_lambda_col, order_type)
        self._query["order"].append(order.query)
        return order
        query: str = ""
        for x in self.__order__:
            if sub_query := self._query.get(x, None):
                query += "\n"
                query += "\n".join([x for x in sub_query])
        
        self._query.clear()
        return query