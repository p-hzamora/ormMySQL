from __future__ import annotations
from typing import Any, Optional, override, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Column
    from ormlambda.engine import Engine

from ormlambda import Table
from ormlambda import BaseRepository
from ormlambda.sql.clauses.interfaces import IDelete
from ormlambda.common.abstract_classes import NonQueryBase
from ormlambda.sql.elements import ClauseElement


class Delete[T: Table, TRepo](NonQueryBase[T, TRepo], IDelete[T], ClauseElement):
    __visit_name__ = "delete"

    def __init__(self, model: T, repository: BaseRepository[TRepo], engine: Engine) -> None:
        super().__init__(model, repository, engine=engine)

    @property
    def CLAUSE(self) -> str:
        return "DELETE"

    @override
    def delete(self, instances: T | list[T]) -> None:
        col: str = ""
        if isinstance(instances, Table):
            pk: Optional[Column] = instances.get_pk()
            if pk is None:
                raise Exception(f"You cannot use 'DELETE' query without set primary key in '{instances.__table_name__}'")
            col = pk.column_name

            pk_value = instances[pk]

            if not pk_value:
                raise ValueError(f"primary key value '{pk_value}' must not be empty.")

            value = str(pk_value)

        elif isinstance(instances, Iterable):
            value: list[Any] = []
            for ins in instances:
                pk = type(ins).get_pk()
                value.append(ins[pk])
            col = pk.column_name

        query: str = f"{self.CLAUSE} FROM {self._model.__table_name__} WHERE {col}"
        if isinstance(value, str):
            query += "= %s"
            self._query = query
            self._values = [value]
            return None

        elif isinstance(value, Iterable):
            params = ", ".join(["%s"] * len(value))
            query += f" IN ({params})"
            self._query = query
            self._values = value
            return None
        else:
            raise Exception(f"'{type(value)}' no esperado")

    @override
    def execute(self) -> None:
        if not self._query:
            raise ValueError
        return self._engine.repository.execute_with_values(self._query, self._values)


__all__ = ["Delete"]
