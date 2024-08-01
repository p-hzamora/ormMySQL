from typing import override
from mysql.connector import Error, errorcode
from ..repository import MySQLRepository

from orm.components.create_database import CreateDatabaseBase, TypeExists


class CreateDatabase(CreateDatabaseBase[MySQLRepository]):
    def __init__(self, repository: MySQLRepository) -> None:
        super().__init__(repository)

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
            else:
                self._repository.database = name
        return None
