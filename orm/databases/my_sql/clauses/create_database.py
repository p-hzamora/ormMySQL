from typing import Literal, override
from mysql.connector import Error, errorcode
from orm.common.interfaces import IRepositoryBase
from mysql.connector import MySQLConnection

TypeExists = Literal["fail", "replace", "append"]


class CreateDatabase:
    def __init__(self, repository: IRepositoryBase[MySQLConnection]) -> None:
        self._repository: IRepositoryBase[MySQLConnection] = repository

    @override
    @property
    def CLAUSE(self) -> str:
        return "CREATE DATABASE"

    @override
    def execute(self, name: str, if_exists: TypeExists = "fail") -> None:
        with self._repository.connection.cursor() as cursor:
            try:
                cursor.execute(f"{self.CLAUSE} {name} DEFAULT CHARACTER SET 'utf8'")
            except Error as err:
                if err.errno == errorcode.ER_DB_CREATE_EXISTS and if_exists != "fail":
                    cursor.execute(f"USE {name};")
                else:
                    raise err
            finally:
                self._repository.set_config({"database":name})
        return None
