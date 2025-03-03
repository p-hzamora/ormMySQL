from typing import Literal, override

from ormlambda.repository import IRepositoryBase

from mysql.connector import MySQLConnection

TypeExists = Literal["fail", "replace", "append"]


class DropTable:
    def __init__(self, repository: IRepositoryBase) -> None:
        self._repository: IRepositoryBase = repository

    @override
    def execute(self, name: str = None) -> None:
        query = rf"{self.CLAUSE} {name}"
        self._repository.execute(query)
        return None

    @property
    @override
    def CLAUSE(self) -> str:
        return "DROP TABLE"
