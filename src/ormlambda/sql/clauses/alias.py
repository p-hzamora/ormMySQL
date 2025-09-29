from __future__ import annotations

from ormlambda import ColumnProxy


class Alias[T](ColumnProxy[T]):
    def __init__(self, column: ColumnProxy[T], alias: str):
        super().__init__(column._column, path=column.path, alias=alias)

    def __repr__(self):
        return f"{Alias.__name__}: {super().__repr__()}"


__all__ = ["Alias"]
