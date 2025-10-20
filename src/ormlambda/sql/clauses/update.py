from __future__ import annotations
from typing import Iterable, Type, overload, Any, TYPE_CHECKING

from ormlambda import Table
from ormlambda.sql.elements import ClauseElement

if TYPE_CHECKING:
    from ormlambda.sql.clauses import Where


class Update[T: Type[Table]](ClauseElement):
    __visit_name__ = "update"

    @overload
    def __init__(self, model: T, where: Where, values: dict[str, Any]) -> None: ...
    @overload
    def __init__(self, model: T, where: Where, values: Iterable[dict[str, Any]]) -> None: ...

    def __init__(self, model: T, where: Where, values) -> None:
        self.values: Iterable[dict[str, Any]] = values if isinstance(values, Iterable) else (values,)
        self.table: Table = model
        self.cleaned_values = []
        self.where: Where = where


__all__ = ["Update"]
