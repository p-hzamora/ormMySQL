from collections import defaultdict
from typing import Callable, Literal, Iterable, Optional

from orm.orm_objects.table import Table
from .where_condition import WhereCondition

OrderQuery = Literal["select", "join", "where", "order", "with", "with_recursive"]


class SQLQuery[T]:
    __order__: tuple[OrderQuery] = ("select", "join", "where", "order", "with", "with_recursive")

    def __init__[T2](self) -> None:
        self._query: dict[OrderQuery, list[str]] = defaultdict(list)

    def where(self): ...
    def select(self): ...
    def join(self): ...

    def build(self):
        query: str = ""
        for x in self.__order__:
            if sub_query := self._query.get(x, None):
                query += "\n"
                query += "\n".join([x for x in sub_query])
        
        self._query.clear()
        return query