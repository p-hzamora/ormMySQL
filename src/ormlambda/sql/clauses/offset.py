from __future__ import annotations
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import ClauseElement

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Offset(IQuery, ClauseElement):
    __visit_name__ = "offset"
    OFFSET = "OFFSET"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number

    @override
    def query(self, dialect: Dialect, **kwargs) -> str:
        return f"{self.OFFSET} {self._number}"


__all__ = ["Offset"]
