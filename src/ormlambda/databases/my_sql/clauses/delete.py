from ormlambda import Table
from ormlambda.repository import IRepositoryBase
from ormlambda.sql.clauses import _Delete
from mysql.connector import MySQLConnection


class DeleteQuery[T: Table](_Delete[T, MySQLConnection]):
    def __init__(self, model: T, repository: IRepositoryBase) -> None:
        super().__init__(model, repository)
