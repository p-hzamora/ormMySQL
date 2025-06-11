from __future__ import annotations
from typing import override, TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda.engine import Engine

from ormlambda import Table
from ormlambda.repository import BaseRepository
from ormlambda.sql.clauses.interfaces import IUpsert
from ormlambda.common.abstract_classes import NonQueryBase
from .insert import Insert
from ormlambda.sql.elements import ClauseElement


class Upsert[T: Table, TRepo](NonQueryBase[T, TRepo], IUpsert[T], ClauseElement):
    __visit_name__ = "upsert"

    def __init__(self, model: T, repository: BaseRepository[TRepo], engine: Engine) -> None:
        super().__init__(model, repository, engine=engine)

    @override
    @property
    def CLAUSE(self) -> str:
        return "ON DUPLICATE KEY UPDATE"

    @override
    def execute(self) -> None:
        return self._engine.repository.executemany_with_values(self._query, self._values)

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
        insert = Insert(self._model, self._engine.repository, self._engine.dialect)
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


__all__ = ["Upsert"]
