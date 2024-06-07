from typing import Callable, overload, Iterable, Optional
from abc import abstractmethod

from orm.orm_objects.table import Table
from .where_condition import WhereCondition


class QuerySelector[T]():
    @overload
    def __init__(
        self,
        orig_table: Table,
    ) -> None: ...

    @overload
    def __init__(
        self,
        where: WhereCondition,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
        where: WhereCondition,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
        select_list: Callable[[T], None],
    ) -> None: ...

    def __init__[T2](
        self,
        orig_table: Table,
        select_list: Callable[[T], None] = lambda: None,
        where: Optional[Callable[[T, T2], bool] | Iterable[Callable[[T, T2], bool]]] = None,
    ) -> None:
        self._orig_table: Table = orig_table
        self._where: WhereCondition = WhereCondition[T, T2](where) if where else None


    @property
    @abstractmethod
    def query(self) -> str: ...
