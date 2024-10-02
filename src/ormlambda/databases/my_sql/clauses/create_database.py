from typing import Literal, override
from mysql.connector import errorcode, errors
from mysql.connector import MySQLConnection

from ormlambda import IRepositoryBase

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
        if self._repository.database_exists(name):
            if if_exists == "replace":
                self._repository.drop_database(name)
            elif if_exists == "fail":
                raise errors.DatabaseError(msg=f"Database '{name}' already exists", errno=errorcode.ER_DB_CREATE_EXISTS)
            elif if_exists == "append":
                counter: int = 0
                char: str = ""
                while self._repository.database_exists(name + char):
                    counter += 1
                    char = f"_{counter}"
                name += char

        query = f"{self.CLAUSE} {name} DEFAULT CHARACTER SET 'utf8'"
        self._repository.execute(query)
        return None
