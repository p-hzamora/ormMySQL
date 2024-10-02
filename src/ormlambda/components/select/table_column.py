from __future__ import annotations
from typing import Any, Iterator
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
    def real_column(self) -> str:
        return self._column

    @property
    def column(self) -> str:
        return f"{self._table.__table_name__}.{self._column} as `{self.alias}`"

    @property
    def alias(self) -> str:
        return f"{self._table.__table_name__}_{self._column}"

    def get_all_alias(self) -> list[str]:
        return [class_.alias for class_ in self.all_columns(self._table)]

    @classmethod
    def all_columns(cls, table: Table) -> Iterator["TableColumn"]:
        for col in table.__annotations__:
            yield cls(table, col)

    def __hash__(self) -> int:
        return hash((self._table, self._column))

    def __eq__(self, __value: Any) -> bool:
        if isinstance(__value, TableColumn):
            return self._table.__table_name__ == __value._table.__table_name__ and self._column == __value._column
        return False
