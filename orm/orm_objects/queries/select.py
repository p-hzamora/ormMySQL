from typing import Callable, overload, Iterable, Optional

from ..table import Table
from .query import QuerySelector
from .condition import Condition


class SelectQuery[T](QuerySelector[T]):
    @overload
    def __init__(
        self,
        table: Table,
        select_list: Callable[[T], None],
    ) -> None: ...

    @overload
    def __init__(
        self,
        table: Table,
        select_list: Iterable[Callable[[T], None]],
    ) -> None: ...

    @overload
    def __init__(
        self,
        table: Table,
        where: Optional[Callable[[T], None]] = None,
    ) -> None: ...

    def __init__[T2](
        self,
        table: Table,
        select_list: Optional[Callable[[T], None] | Iterable[Callable[[T], None]]] = None,
        where: Optional[Callable[[T, T2], bool]] = None,
    ) -> None:
        super().__init__(table, select_list, where=where)

        self._where: Optional[Condition[T, T2]] = Condition[T, T2](where) if where else None

    @property
    def query(self) -> str:
        query = f"SELECT {self._select_str} FROM {self._orig_table.__table_name__}"
        if self._where:
            query += f" {self._where.to_query()}"
        return query

