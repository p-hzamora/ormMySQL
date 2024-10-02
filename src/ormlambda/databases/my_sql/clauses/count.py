from typing import Type, override

from ormlambda.common.abstract_classes.non_query_base import NonQueryBase
from ormlambda.common.interfaces.IRepositoryBase import IRepositoryBase
from ormlambda.utils.table_constructor import Table
from mysql.connector import MySQLConnection


class CountQuery[T:Type[Table]](NonQueryBase[T, IRepositoryBase[MySQLConnection]]):
    CLAUSE: str = "COUNT"

    def __init__(self, model: T, repository: IRepositoryBase[MySQLConnection]) -> None:
        super().__init__(model, repository)

    @override
    @property
    def query(self) -> str:
        return f"SELECT {self.CLAUSE}(*) FROM {self._model.__table_name__}"

    @override
    def execute(self) -> int:
        if not self.query:
            raise ValueError
        return self._repository.read_sql(self.query)
