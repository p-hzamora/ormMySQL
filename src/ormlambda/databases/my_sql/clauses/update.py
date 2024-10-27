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

        name_cols: list[Column] = []

        for col, value in dicc.items():
            col: Column = self._model.get_column(col, value)

            if self.__is_valid__(col):
                name_cols.append(col)
                self._values.append(col.column_value_to_query)

        set_query: str = ",".join(["=".join([col.column_name, col.placeholder]) for col in name_cols])

        self._query = f"{self.CLAUSE} {self._model.__table_name__} SET {set_query}"
        self._values = tuple(self._values)
        return None

    def __is_valid__(self, col: Column) -> bool:
        return not col.is_auto_generated
