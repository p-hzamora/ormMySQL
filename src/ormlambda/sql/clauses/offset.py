from typing import override

from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import ClauseElement


class Offset(IQuery, ClauseElement):
    __visit_name__ = "offset"
    OFFSET = "OFFSET"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number


    @override
    @property
    def query(self) -> str:
        return f"{self.OFFSET} {self._number}"


__all__ = ["Offset"]
