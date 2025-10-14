from __future__ import annotations
from typing import Iterable, Type, overload, Any

from ormlambda import Table
from ormlambda.sql.elements import ClauseElement



class Update[T: Type[Table]](ClauseElement):
    __visit_name__ = "update"

    @overload
    def __init__(self, model: T, values: dict[str, Any]) -> None: ...
    @overload
    def __init__(self, model: T, values: Iterable[dict[str, Any]]) -> None: ...

    def __init__(self, model: T, values) -> None:
        self.values: Iterable[dict[str, Any]] = values if isinstance(values, Iterable) else (values,)
        self.table:Table = model
        self.cleaned_values = []


__all__ = ["Update"]
