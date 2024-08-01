from typing import override

from orm.components.drop_database import DropDatabaseBase
from ..repository import MySQLRepository


class DropDatabase(DropDatabaseBase[MySQLRepository]):
    def __init__(self, repository: MySQLRepository) -> None:
        super().__init__(repository)

    @override
    def execute(self, name: str) -> None:
        return self._repository.execute(f"{self.CLAUSE} {name}")

    @override
    @property
    def CLAUSE(self) -> str:
        return "DROP DATABASE IF EXISTS"
