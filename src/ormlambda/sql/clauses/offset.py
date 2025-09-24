from __future__ import annotations
from ormlambda.sql.elements import ClauseElement


class Offset(ClauseElement):
    __visit_name__ = "offset"

    def __init__(self, number: tuple[int]) -> None:
        # FIXME []: check this validation when I finished to refactor. Same process in Limit class
        # if not isinstance(number, int):
        #     raise ValueError
        self._number: int = number


__all__ = ["Offset"]
