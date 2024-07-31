from typing import Literal
from orm.interfaces import IQuery, IRepositoryBase
from mysql.connector import Error, MySQLConnection, errorcode
from ..repository import MySQLRepository

TypeExists = Literal["fail", "replace", "append"]

class CreateDatabase():
    def __init__(self, repository: IRepositoryBase[MySQLConnection]) -> None:
        self._repository: IRepositoryBase[MySQLConnection] = repository

    @MySQLRepository._is_connected
    def execute(self, db_name: str, if_exists: TypeExists = "fail") -> None:
        self._database = db_name
        with self._repository.connection.cursor() as cursor:
            try:
                cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
            except Error as err:
                if err.errno == errorcode.ER_DB_CREATE_EXISTS and if_exists != "fail":
                    cursor.execute(f"USE {db_name};")
                else:
                    raise err
            finally:
                self.database = db_name
        return None