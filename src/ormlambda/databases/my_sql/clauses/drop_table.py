from __future__ import annotations
from typing import Literal, override, TYPE_CHECKING

if TYPE_CHECKING:
    from mysql.connector import MySQLConnection

from ormlambda.repository import BaseRepository


TypeExists = Literal["fail", "replace", "append"]


class DropTable:
    def __init__(self, repository: BaseRepository[MySQLConnection]) -> None:
        self._repository: BaseRepository[MySQLConnection] = repository

    @override
    def execute(self, name: str = None) -> None:
        query = rf"{self.CLAUSE} {name}"
        self._repository.execute(query)
        return None

    @property
    @override
    def CLAUSE(self) -> str:
        return "DROP TABLE"
