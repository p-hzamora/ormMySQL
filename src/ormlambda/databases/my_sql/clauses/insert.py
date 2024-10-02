from typing import Any, override, Iterable
from mysql.connector import MySQLConnection

from ormlambda import Table
from ormlambda import Column
from ormlambda.components.insert import InsertQueryBase
from ormlambda import IRepositoryBase


class InsertQuery[T: Table](InsertQueryBase[T, IRepositoryBase[MySQLConnection]]):
    def __init__(self, model: T, repository: IRepositoryBase[IRepositoryBase[MySQLConnection]]) -> None:
        super().__init__(model, repository)

    @override
    @property
    def CLAUSE(self) -> str:
        return "INSERT INTO"

    @override
    def execute(self) -> None:
        if not self._query:
            raise ValueError
        return self._repository.executemany_with_values(self.query, self._values)

    @override
    def insert(self, instances: T | list[T]) -> None:
        new_dict_list: list[dict[str, Any]] = []
        self.__fill_dict_list(new_dict_list, instances)
        cols_tuple = new_dict_list[0].keys()
        join_cols = ", ".join(cols_tuple)
        unknown_rows = f'({", ".join(["%s"]*len(cols_tuple))})'  # The number of "%s" must match the dict 'dicc_0' length

        self._values = [tuple(x.values()) for x in new_dict_list]
        self._query = f"{self.CLAUSE} {self._model.__table_name__} {f'({join_cols})'} VALUES {unknown_rows}"
        return None

    @staticmethod
    def __is_valid(column: Column) -> bool:
        """
        We want to delete the column from table when it's specified with an 'AUTO_INCREMENT' or 'AUTO GENERATED ALWAYS AS (__) STORED' statement.

        if the column is auto-generated, it means the database creates the value for that column, so we must deleted it.
        if the column is primary key and auto-increment, we should be able to create an object with specific pk value.

        RETURN
        -----

        - True  -> Do not delete the column from dict query
        - False -> Delete the column from dict query
        """

        is_pk_none_and_auto_increment: bool = all([column.column_value is None, column.is_primary_key, column.is_auto_increment])

        if is_pk_none_and_auto_increment or column.is_auto_generated:
            return False
        return True

    def __fill_dict_list(self, list_dict: list[dict], values: T | list[T]):
        if issubclass(values.__class__, Table):
            dicc: dict = {}
            for col in values.__dict__.values():
                if isinstance(col, Column) and self.__is_valid(col):
                    dicc.update({col.column_name: col.column_value})
            list_dict.append(dicc)
            return list_dict

        elif isinstance(values, Iterable):
            for x in values:
                self.__fill_dict_list(list_dict, x)
        else:
            raise Exception(f"Tipo de dato'{type(values)}' no esperado")
