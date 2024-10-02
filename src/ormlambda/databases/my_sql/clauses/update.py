from typing import Type, override, Any
from mysql.connector import MySQLConnection

from ormlambda.components.update import UpdateQueryBase
from ormlambda import Table, Column
from ormlambda import IRepositoryBase
from .where_condition import WhereCondition


class UpdateQuery[T: Type[Table]](UpdateQueryBase[T, IRepositoryBase[MySQLConnection]]):
    def __init__(self, model: T, repository: Any, where: list[WhereCondition]) -> None:
        super().__init__(model, repository, where)

    @override
    @property
    def CLAUSE(self) -> str:
        return "UPDATE"

    @override
    def execute(self) -> None:
        if self._where:
            self._query += " " + WhereCondition.join_condition(*self._where)
        return self._repository.execute_with_values(self._query, self._values)

    @override
    def update(self, dicc: Any | dict[str | property, Any]) -> None:
        if not isinstance(dicc, dict):
            raise TypeError

        name_cols: list[str] = []

        for col, value in dicc.items():
            if isinstance(col, str):
                string_col = col
            else:
                string_col = self._model.__properties_mapped__.get(col, None)
                if not string_col:
                    raise KeyError(f"Class '{self._model.__name__}' has not {col} mapped.")
            if self.__is_valid__(string_col, value):
                name_cols.append(string_col)
                self._values.append(value)

        set_query: str = ",".join(["=".join([col, "%s"]) for col in name_cols])

        self._query = f"{self.CLAUSE} {self._model.__table_name__} SET {set_query}"
        return None

    def __is_valid__(self, col: str, value: Any) -> bool:
        instance_table: Table = self._model(**{col: value})

        column: Column = getattr(instance_table, f"_{col}")
        return not column.is_auto_generated
