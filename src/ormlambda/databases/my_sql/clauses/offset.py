from typing import override

from ormlambda.common.interfaces.IQueryCommand import IQuery


class OffsetQuery(IQuery):
    OFFSET = "OFFSET"

    def __init__(self, number: int) -> None:
        if not isinstance(number, int):
            raise ValueError
        self._number: int = number

    @override
    @property
    def query(self) -> str:
        return f"{self.OFFSET} {self._number}"
