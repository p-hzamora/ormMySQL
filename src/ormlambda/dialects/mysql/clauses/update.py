from mysql.connector import MySQLConnection

from ormlambda.sql.clauses import Update


class Update[T](Update[T, MySQLConnection]):
    def __init__(self, model, repository, where):
        super().__init__(model, repository, where)
