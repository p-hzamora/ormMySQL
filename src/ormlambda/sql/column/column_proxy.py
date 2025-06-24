from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ormlambda.sql.column_table_proxy import ColumnTableProxy


if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from .column import Column
    from ormlambda.sql.context import FKChain


class ColumnProxy(ColumnTableProxy):
    _column: Column
    _path: FKChain

    def __init__(self, column: Column, path: FKChain):
        self._column = column
        super().__init__(path)


    def __str__(self) -> str:
        return self._get_full_reference()

    def __repr__(self) -> str:
        return f"{ColumnProxy.__name__}({self._column.table.__table_name__}.{self._column.column_name}) Path={self._path.get_path_key()}"

    def __getattr__(self, name: str):
        # it does not work when comparing methods
        return getattr(self._column, name)

    def __eq__(self, other: Any) -> Comparer:
        return self._column.__eq__(other)

    def __ne__(self, other: Any) -> Comparer:
        return self._column.__ne__(other)

    def __lt__(self, other: Any) -> Comparer:
        return self._column.__lt__(other)

    def __le__(self, other: Any) -> Comparer:
        return self._column.__le__(other)

    def __gt__(self, other: Any) -> Comparer:
        return self._column.__gt__(other)

    def __ge__(self, other: Any) -> Comparer:
        return self._column.__ge__(other)

    def _get_full_reference(self):
        from ormlambda import ForeignKey

        alias: list[str] = [self._path.base.__table_name__]
        base = self._path.base

        n = len(self._path.steps)

        for i in range(n):
            attr = self._path.steps[i]

            # last element
            if i == n - 1:
                value = attr._column.column_name

            else:
                value = attr.clause_name
            alias.append(value)

        return ".".join(alias)

    def get_alias(self) -> str:
        return self._path.get_alias()

