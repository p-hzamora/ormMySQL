from __future__ import annotations
from typing import Type, override, Any, TYPE_CHECKING, Optional

from ormlambda import Table, Column
from ormlambda.caster.caster import Caster
from .where import Where
from ormlambda.common.abstract_classes import NonQueryBase
from .interfaces import IUpdate

if TYPE_CHECKING:
    from ormlambda.sql.types import ColumnType
    from .where import Where
    from ormlambda.engine import Engine

from ormlambda.sql.elements import ClauseElement


class UpdateKeyError(KeyError):
    def __init__(self, table: Type[Table], key: str | ColumnType, *args):
        super().__init__(*args)
        self._table: Type[Table] = table
        self._key: str | ColumnType = key

    def __str__(self):
        if isinstance(self._key, Column):
            return f"The column '{self._key.column_name}' does not belong to the table '{self._table.__table_name__}'; it belongs to the table '{self._key.table.__table_name__}'. Please check the columns in the query."
        return f"The column '{self._key}' does not belong to the table '{self._table.__table_name__}'. Please check the columns in the query."


class Update[T: Type[Table], TRepo](NonQueryBase[T, TRepo], IUpdate, ClauseElement):
    __visit_name__ = "update"

    def __init__(self, model: T, repository: Any, where: list[Where], engine: Engine) -> None:
        super().__init__(model, repository, engine=engine)
        self._where: Optional[list[Where]] = where

    @override
    @property
    def CLAUSE(self) -> str:
        return "UPDATE"

    @override
    def execute(self) -> None:
        if self._where:
            for where in self._where:
                query_with_table = where.query(self._engine.dialect)
                for x in where._comparer:
                    # TODOH []: Refactor this part. We need to get only the columns withouth __table_name__ preffix
                    self._query += " " + query_with_table.replace(x.left_condition(self._dialect).table.__table_name__ + ".", "")
        return self._engine.repository.execute_with_values(self._query, self._values)

    @override
    def update[TProp](self, dicc: dict[str | ColumnType[TProp], Any]) -> None:
        if not isinstance(dicc, dict):
            raise TypeError

        col_names: list[Column] = []
        CASTER = self._engine.dialect.caster()
        for col, value in dicc.items():
            if isinstance(col, str):
                if not hasattr(self._model, col):
                    raise UpdateKeyError(self._model, col)
                col = getattr(self._model, col)
            if not isinstance(col, Column):
                raise ValueError

            if self.__is_valid__(col):
                clean_data = CASTER.for_value(value)
                col_names.append((col.column_name, clean_data.wildcard_to_insert()))
                self._values.append(clean_data.to_database)

        set_query: str = ",".join(["=".join(col_data) for col_data in col_names])

        self._query = f"{self.CLAUSE} {self._model.__table_name__} SET {set_query}"
        self._values = tuple(self._values)
        return None

    def __is_valid__(self, col: Column) -> bool:
        if self._model is not col.table:
            raise UpdateKeyError(self._model, col)
        return not col.is_auto_generated


__all__ = ["Update"]
