from typing import override
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import ClauseElement


class Limit(ClauseElement, IQuery):
    __visit_name__ = "limit"
    LIMIT = "LIMIT"

    def __init__(self, number: int, **kwargs) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number

    @override
    @property
    def query(self) -> str:
        return f"{self.LIMIT} {self._number}"


__all__ = ["Limit"]
