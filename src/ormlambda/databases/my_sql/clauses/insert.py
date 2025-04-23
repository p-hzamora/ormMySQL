from __future__ import annotations
from ormlambda import Table
from ormlambda.sql.clauses import _Insert
from mysql.connector import MySQLConnection


class InsertQuery[T: Table](_Insert[T, MySQLConnection]):
    def __init__(self, model, repository):
        super().__init__(model, repository)
