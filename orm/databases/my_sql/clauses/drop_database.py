from orm.common.interfaces import IQuery, IRepositoryBase
from mysql.connector import Error, MySQLConnection

from ..repository import MySQLRepository


class DropDatabase(IQuery):
    DROP: str = "DROP DATABASE IF EXISTS"

    def __init__(self, repository: IRepositoryBase[MySQLConnection]) -> None:
        self._repository: IRepositoryBase[MySQLConnection] = repository

    @MySQLRepository._is_connected
    def execute(self, db_name: str) -> None:
        try:
            with self._repository.connection.cursor() as cursor:
                cursor.execute(f"{self.DROP} {db_name}")
        except Error as err:
            raise err
