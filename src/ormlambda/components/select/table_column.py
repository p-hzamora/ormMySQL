from __future__ import annotations
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Table


class TableColumn:
    def __init__(self, table: Table, col: str) -> None:
        self._table: Table = table
        self._column: str = col

    def __repr__(self) -> str:
        return f"{TableColumn.__name__}: T={self._table.__table_name__} col={self._column}"

    @property
    def column(self) -> str:
        return self._column

    def __hash__(self) -> int:
        return hash((self._table, self._column))

    def __eq__(self, __value: Any) -> bool:
        if isinstance(__value, TableColumn):
            return self._table.__table_name__ == __value._table.__table_name__ and self._column == __value._column
        return False
