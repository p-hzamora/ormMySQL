from typing import override

from ormlambda.common.interfaces.IQueryCommand import IQuery


class LimitQuery(IQuery):
    LIMIT = "LIMIT"

    def __init__(self, number: int) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number

    @override
    @property
    def query(self) -> str:
        return f"{self.LIMIT} {self._number}"
