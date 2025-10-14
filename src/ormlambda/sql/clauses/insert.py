from __future__ import annotations

from typing import Iterable, overload

from ormlambda import Table

from ormlambda.sql.elements import ClauseElement


class Insert[T: Table](ClauseElement):
    __visit_name__ = "insert"

    @overload
    def __init__(self, values: list[T]) -> None: ...
    @overload
    def __init__(self, values: T) -> None: ...

    def __init__(self, values: T | list[T]) -> None:
        self.values:Iterable[T] = values if isinstance(values, Iterable) else (values,)
        self.table = type(self.values[0])

        self.cleaned_values = []


__all__ = ["Insert"]
