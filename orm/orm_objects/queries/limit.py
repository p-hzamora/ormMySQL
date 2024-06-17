from typing import override

from ...interfaces.IQuery import IQuery


class LimitQuery(IQuery):
    LIMIT = "LIMIT"

    def __init__(self, number: int) -> None:
        self._number: int = number

    @override
    @property
    def query(self) -> str:
        return f"{self.LIMIT} {self._number}"
