from typing import override, Callable, overload, Optional
from enum import Enum

from ..table import Table

from .query import IQuery
from orm.dissambler import Dissambler


class JoinType(Enum):
    RIGHT_INCLUSIVE = "RIGHT JOIN"
    LEFT_INCLUSIVE = "LEFT JOIN"
    RIGHT_EXCLUSIVE = "RIGHT JOIN"
    LEFT_EXCLUSIVE = "LEFT JOIN"
    FULL_OUTER_INCLUSIVE = "RIGHT JOIN"
    FULL_OUTER_EXCLUSIVE = "RIGHT JOIN"
    INNER_JOIN = "INNER JOIN"


class JoinSelector[TLeft, TRight](IQuery):
    @overload
    def __init__(
        self,
        table_left: TLeft,
        table_right: TRight,
        col_left: str,
        col_right: str,
        by: JoinType,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: TLeft,
        table_right: TRight,
        by: JoinType,
        where: Callable[[TLeft, TRight], bool],
    ) -> None: ...

    def __init__(
        self,
        table_left: Table,
        table_right: Table,
        by: JoinType,
        col_left: Optional[str] = None,
        col_right: Optional[str] = None,
        where: Optional[Callable[[TLeft, TRight], bool]] = None,
    ) -> None:
        self._orig_table: Table = table_left
        self._table_right: Table = table_right
        self._by: JoinType = by

        if all(x is None for x in (col_left, col_right, where)):
            raise ValueError("You must specify at least 'where' clausule or ('_left_col',_right_col')")

        if where is None:
            self._left_col:str = col_left
            self._right_col:str = col_right
            self._compareop:str = "="
        else:
            _dis: Dissambler[TLeft, TRight] = Dissambler[TLeft, TRight](where)
            self._left_col:str = _dis.cond_1.name
            self._right_col:str = _dis.cond_2.name
            self._compareop:str = _dis.compare_op

    @property
    @override
    def query(self) -> str:
        # {inner join} table_name on
        #   table_name.first col = table_name.second_col

        left_col = f"{self._orig_table.__table_name__}.{self._left_col}"
        right_col = f"{self._table_right.__table_name__}.{self._right_col}"
        list_ = [
            self._by.value,  # inner join
            self._table_right.__table_name__,  # table_name
            "ON",
            left_col,  # first_col
            self._compareop,  # =
            right_col,  # second_col
        ]
        return " ".join(list_)
