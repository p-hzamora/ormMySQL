from typing import override
from mysql.connector import MySQLConnection


from ormlambda import IRepositoryBase


class DropDatabase:
    def __init__(self, repository: IRepositoryBase[MySQLConnection]) -> None:
        self._repository: IRepositoryBase[MySQLConnection] = repository

    @override
    def execute(self, name: str) -> None:
        return self._repository.execute(f"{self.CLAUSE} {name}")

    @override
    @property
    def CLAUSE(self) -> str:
        return "DROP DATABASE IF EXISTS"
