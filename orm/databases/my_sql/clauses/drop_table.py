from typing import Literal, override

from orm.common.interfaces import IRepositoryBase
from orm.components.drop_table import DropTableBase

from orm.utils import Table
from ..repository import MySQLRepository

TypeExists = Literal["fail", "replace", "append"]


class DropTable[T: Table, TRepo: IRepositoryBase](DropTableBase[T, TRepo]):
    def __init__(self, repository: MySQLRepository) -> None:
        self._repository: MySQLRepository = repository

    @override
    def execute(self, name: str = None) -> None:
        tbl_name = self._model.__table_name__ if not name else name
        query = rf"{self.CLAUSE} {tbl_name}"
        self._repository.execute(query)
        return None

    @property
    @override
    def CLAUSE(self) -> str:
        return "DROP TABLE"
