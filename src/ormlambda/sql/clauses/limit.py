from __future__ import annotations
from typing import override
from typing import TYPE_CHECKING
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import ClauseElement

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Limit(ClauseElement, IQuery):
    __visit_name__ = "limit"
    LIMIT = "LIMIT"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number

    @override
    def query(self, dialect: Dialect, **kwargs) -> str:
        return f"{self.LIMIT} {self._number}"


__all__ = ["Limit"]
