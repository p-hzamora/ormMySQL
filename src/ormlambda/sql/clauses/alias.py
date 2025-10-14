from __future__ import annotations

from ormlambda import ColumnProxy
from ormlambda.sql.comparer import Comparer


class Alias[T](ColumnProxy[T]):
    def __new__(cls, object: ColumnProxy | Comparer, alias: str):
        if not isinstance(object, ColumnProxy):
            return ComparerAlias(object, alias)
        return ColumnAlias(object, alias)

    def __repr__(self):
        return f"{Alias.__name__}: {super().__repr__()}"


class ColumnAlias[T](ColumnProxy[T]):
    def __init__(self, column: ColumnProxy[T], alias: str):
        super().__init__(column._column, path=column.path, alias=alias)

    def __repr__(self):
        return f"{Alias.__name__}: {super().__repr__()}"


class ComparerAlias(Comparer):
    def __init__(
        self,
        comparer: Comparer,
        alias: str,
    ):
        super().__init__(
            left_condition=comparer.left_condition,
            right_condition=comparer.right_condition,
            compare=comparer.compare,
            flags=comparer.flags,
            alias=alias,
        )

    def __repr__(self):
        return f"{ComparerAlias.__name__}: {super().__repr__()}"


__all__ = ["Alias"]
