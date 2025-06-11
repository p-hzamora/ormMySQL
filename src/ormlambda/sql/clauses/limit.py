from __future__ import annotations
from ormlambda.sql.elements import ClauseElement


class Limit(ClauseElement):
    __visit_name__ = "limit"
    LIMIT = "LIMIT"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number


__all__ = ["Limit"]
