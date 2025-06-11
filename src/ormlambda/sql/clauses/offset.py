from __future__ import annotations
from ormlambda.sql.elements import ClauseElement


class Offset(ClauseElement):
    __visit_name__ = "offset"
    OFFSET = "OFFSET"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number


__all__ = ["Offset"]
