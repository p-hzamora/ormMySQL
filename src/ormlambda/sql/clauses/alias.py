from __future__ import annotations
from typing import cast

from ormlambda import ColumnProxy
from ormlambda.sql.comparer import IComparer, UnionEnum
from ormlambda.sql.elements import ClauseElement


class Alias[T](ColumnProxy[T]):
    def __new__(cls, object: ColumnProxy | IComparer, alias: str):
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


class ComparerAlias(IComparer):
    __visit_name__ = "comparer_alias"

    def __init__(
        self,
        comparer: IComparer,
        alias: str,
    ):
        self.comparer = comparer
        self.alias = alias

    def __repr__(self):
        return f"{ComparerAlias.__name__}: {self.comparer.__repr__()}"

    def used_columns(self):
        return self.comparer.used_columns()

    @property
    def join(self) -> UnionEnum:
        return self.comparer.join

    def compile(self, dialect=None, **kw):
        return cast(ClauseElement,self.comparer).compile(dialect, **kw)


__all__ = ["Alias"]
