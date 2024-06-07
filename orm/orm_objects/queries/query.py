from collections import defaultdict
from typing import Callable, overload, Iterable, Optional
from abc import abstractmethod

from orm.orm_objects.table import Table
from .where_condition import WhereCondition


class QuerySelector[T]():
    __order__:tuple[str] = ("select", "join", "where", "order","with","with_recursive")

    def __init__[T2](
        self,
        orig_table: Table,
        select_list: Callable[[T], None] = lambda: None,
        where: Optional[Callable[[T, T2], bool] | Iterable[Callable[[T, T2], bool]]] = None,
    ) -> None:
        self._orig_table: Table = orig_table
        self._where: WhereCondition = WhereCondition[T, T2](where) if where else None
        self._query = defaultdict(list)


    @property
    @abstractmethod
    def query(self) -> str: ...
