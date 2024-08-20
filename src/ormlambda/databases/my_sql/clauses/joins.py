from typing import override, Callable, overload, Optional, TypeVar

# from ..table import Table

from ....common.interfaces.IQueryCommand import IQuery
from ....utils.lambda_disassembler import Disassembler
from ....common.enums import JoinType

# TODOL: Try to import Table module without circular import Error
Table = TypeVar("Table")


class JoinSelector[TLeft, TRight](IQuery):
    __slots__: tuple = (
        "_orig_table",
        "_table_right",
        "_by",
        "_left_col",
        "_right_col",
        "_compareop",
    )

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
            self._left_col: str = col_left
            self._right_col: str = col_right
            self._compareop: str = "="
        else:
            _dis: Disassembler[TLeft, TRight] = Disassembler[TLeft, TRight](where)
            self._left_col: str = _dis.cond_1.name
            self._right_col: str = _dis.cond_2.name
            self._compareop: str = _dis.compare_op

    def __eq__(self, __value: "JoinSelector") -> bool:
        return isinstance(__value, JoinSelector) and self.__hash__() == __value.__hash__()

    def __hash__(self) -> int:
        return hash(
            (
                self._orig_table,
                self._table_right,
                self._by,
                self._left_col,
                self._right_col,
                self._compareop,
            )
        )

    @classmethod
    def join_selectors(cls, *args: "JoinSelector") -> str:
        return "\n".join([x.query for x in args])

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
