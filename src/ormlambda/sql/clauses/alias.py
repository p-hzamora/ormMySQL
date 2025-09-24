from __future__ import annotations

from ormlambda import ColumnProxy


class Alias[T](ColumnProxy[T]):
    def __init__(self, column: ColumnProxy[T], alias: str):
        super().__init__(column._column, path=column.path, alias=alias)


__all__ = ["Alias"]
