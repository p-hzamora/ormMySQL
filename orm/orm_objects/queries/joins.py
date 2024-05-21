from typing import Any, override, Callable, overload, Iterable, Optional
from enum import Enum

from ..table import Table

from .query import QuerySelector
from .select import SelectQuery
from .query import get_var_from_lambda


class JoinType(Enum):
    RIGHT_INCLUSIVE = "RIGHT JOIN"
    LEFT_INCLUSIVE = "LEFT JOIN"
    RIGHT_EXCLUSIVE = "RIGHT JOIN"
    LEFT_EXCLUSIVE = "LEFT JOIN"
    FULL_OUTER_INCLUSIVE = "RIGHT JOIN"
    FULL_OUTER_EXCLUSIVE = "RIGHT JOIN"
    INNER_JOIN = "INNER JOIN"


class JoinSelector[TLeft, TRight](QuerySelector[TLeft]):
    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        select_list: Optional[Callable[[TLeft], None]] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        select_list: Optional[Iterable[Callable[[TLeft], None]]] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        where: Optional[Callable[[TLeft, TRight], bool]] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        where: Optional[Iterable[Callable[[TLeft, TRight], bool]]] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        where: Optional[Callable[[TLeft, Any], bool]] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        where: Optional[Iterable[Callable[[TLeft, Any], bool]]] = None,
    ) -> None: ...

    def __init__(
        self,
        table_left: Table,
        col_left: Callable[[TLeft], None],
        table_right: Table,
        col_right: Callable[[TRight], None],
        by: JoinType,
        select_list: Optional[Callable[[TLeft], None] | Iterable[Callable[[TLeft], None]]] = None,
        where: Optional[Callable[[TLeft, TRight], bool] | Iterable[Callable[[TLeft, TRight], bool]]] = None,
    ) -> None:
        super().__init__(table_left, select_list, where=where)
        self._table_right: Table = table_right
        self._by: JoinType = by
        self._col_left: str = get_var_from_lambda(col_left)
        self._col_right: str = get_var_from_lambda(col_right)

    @property
    @override
    def query(self) -> str:
        select = SelectQuery[TLeft](self._orig_table, self._select_list)

        return f"{select.query} {self._by.value} {self._table_right.__table_name__} ON {self._orig_table.__table_name__}.{self._col_left} = {self._table_right.__table_name__}.{self._col_right}"
