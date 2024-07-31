from typing import Literal
from orm.interfaces import IQuery, IRepositoryBase
from mysql.connector import MySQLConnection
from ..repository import MySQLRepository

TypeExists = Literal["fail", "replace", "append"]


class DropTable:
    DROP: str = "DROP TABLE"

    def __init__(self, repository: IRepositoryBase[MySQLConnection]) -> None:
        self._repository: IRepositoryBase[MySQLConnection] = repository

    @MySQLRepository._is_connected
    def drop_table(self, name: str) -> bool:
        query = rf"{self.DROP} {name}"

        # CONSULTA A LA BBDD
        with self._repository.connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            self._repository.connection.commit()
        return True
