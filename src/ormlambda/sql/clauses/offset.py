from __future__ import annotations
from ormlambda.sql.elements import ClauseElement


class Offset(ClauseElement):
    __visit_name__ = "offset"
    OFFSET = "OFFSET"

    def __init__(self, number: tuple[int], **kwargs) -> None:
        # FIXME []: check this validation when I finished to refactor. Same process in Limit class
        # if not isinstance(number, int):
        #     raise ValueError
        self._number: int = number[0]


__all__ = ["Offset"]
