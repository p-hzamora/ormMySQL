from typing import Literal, override
from mysql.connector import Error, errorcode
from ..repository import MySQLRepository

from orm.common.abstract_classes.non_query_base import NonQueryBase

TypeExists = Literal["fail", "replace", "append"]


class CreateDatabase[T](NonQueryBase[T, MySQLRepository]):
    def __init__(self, model: T, repository: MySQLRepository) -> None:
        super().__init__(model, repository)

    @MySQLRepository._is_connected
    def _execute(self, db_name: str, if_exists: TypeExists = "fail") -> None:
        self._database = db_name
        with self._repository.connection.cursor() as cursor:
            try:
                cursor.execute(f"{self.CLAUSE} {db_name} DEFAULT CHARACTER SET 'utf8'")
            except Error as err:
                if err.errno == errorcode.ER_DB_CREATE_EXISTS and if_exists != "fail":
                    cursor.execute(f"USE {db_name};")
                else:
                    raise err
            finally:
                self.database = db_name
        return None

    @override
    @property
    def CLAUSE(self) -> str:
        return "CREATE DATABASE"

    @override
    def execute(self) -> None:
        self._execute()
