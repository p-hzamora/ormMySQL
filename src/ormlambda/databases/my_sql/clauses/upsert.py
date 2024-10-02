from typing import override, Any

from ormlambda import Table
from ormlambda.components.upsert import UpsertQueryBase
from ormlambda import IRepositoryBase
from mysql.connector import MySQLConnection

from .insert import InsertQuery


class UpsertQuery[T: Table](UpsertQueryBase[T, IRepositoryBase[MySQLConnection]]):
    def __init__(self, model: T, repository: Any) -> None:
        super().__init__(model, repository)

    @override
    @property
    def CLAUSE(self) -> str:
        return "ON DUPLICATE KEY UPDATE"

    @override
    def execute(self) -> None:
        return self._repository.executemany_with_values(self._query, self._values)

    @override
    def upsert(self, instances: T | list[T]) -> None:
        """
        Esta funcion se enfoca para trabajar con listas, aunque el argumneto changes sea un unico diccionario.

        Accedemos a la primera posicion de la lista 'changes[0]' porque en la query solo estamos poniendo marcadores de posicion, alias y nombres de columnas

        EXAMPLE
        ------

        MySQL
        -----

        INSERT INTO NAME_TABLE(PK_COL,COL2)
        VALUES
        (1,'PABLO'),
        (2,'MARINA') AS _val
        ON DUPLICATE KEY UPDATE
        COL2 = _val.COL2;

        Python
        -----

        INSERT INTO NAME_TABLE(PK_COL,COL2)
        VALUES (%s, %s') AS _val
        ON DUPLICATE KEY UPDATE
        COL2 = _val.COL2;

        """
        insert = InsertQuery[T](self._model, self._repository)
        insert.insert(instances)

        if isinstance(instances, Table):
            instances = tuple([instances])
        ALIAS = "VALUES"

        cols = instances[0].get_columns()
        pk_key = instances[0].get_pk().column_name

        alternative = ", ".join([f"{col}={ALIAS}({col})" for col in cols if col != pk_key])
        query = f"{insert._query} {self.CLAUSE} {alternative};"

        self._query = query
        self._values = insert.values
        return None
