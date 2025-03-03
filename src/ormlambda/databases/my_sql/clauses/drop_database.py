from typing import override

from ormlambda.repository import IRepositoryBase


class DropDatabase:
    def __init__(self, repository: IRepositoryBase) -> None:
        self._repository: IRepositoryBase = repository

    @override
    def execute(self, name: str) -> None:
        return self._repository.execute(f"{self.CLAUSE} {name}")

    @override
    @property
    def CLAUSE(self) -> str:
        return "DROP DATABASE IF EXISTS"
