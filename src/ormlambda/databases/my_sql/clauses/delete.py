from ormlambda import Table
from ormlambda.repository import IRepositoryBase
from ormlambda.sql.clauses import Delete
from mysql.connector import MySQLConnection


class DeleteQuery[T: Table](Delete[T, MySQLConnection]):
    def __init__(self, model: T, repository: IRepositoryBase) -> None:
        super().__init__(model, repository)
