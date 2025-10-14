from __future__ import annotations
from typing import Iterable, overload
from ormlambda.sql.elements import ClauseElement
from ormlambda import Table


class Delete[T: Table](ClauseElement):
    __visit_name__ = "delete"

    @overload
    def __init__(self, table: T, values: T) -> None: ...
    @overload
    def __init__(self, table: T, values: Iterable[T]) -> None: ...

    def __init__(self, table: T, values) -> None:
        self.values: Table | Iterable[Table] = values
        self.table = table
        self.cleaned_values = []


__all__ = ["Delete"]
