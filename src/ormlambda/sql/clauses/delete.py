from __future__ import annotations
from typing import Iterable, overload, TYPE_CHECKING
from ormlambda.sql.elements import ClauseElement
from ormlambda import Table

if TYPE_CHECKING:
    from ormlambda.sql.clauses import Where


class Delete[T: Table](ClauseElement):
    __visit_name__ = "delete"

    @overload
    def __init__(self, table: T, where: Where, values: T) -> None: ...
    @overload
    def __init__(self, table: T, where: Where, values: Iterable[T]) -> None: ...

    def __init__(self, table: T, where: Where, values) -> None:
        self.values: Table | Iterable[Table] = values
        self.table = table
        self.cleaned_values = []
        self.where = where


__all__ = ["Delete"]
