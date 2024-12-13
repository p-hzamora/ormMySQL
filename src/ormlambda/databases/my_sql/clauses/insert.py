from typing import override, Iterable
from mysql.connector import MySQLConnection

from ormlambda import Table
from ormlambda import Column
from ormlambda.components.insert import InsertQueryBase
from ormlambda import IRepositoryBase
from ..casters import MySQLWriteCastBase


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
        valid_cols: list[list[Column]] = []
        self.__fill_dict_list(valid_cols, instances)

        col_names: list[str] = []
        wildcards: list[str] = []
        col_values: list[list[str]] = []
        for i, cols in enumerate(valid_cols):
            col_values.append([])
            for col in cols:
                if i == 0:
                    col_names.append(col.column_name)
                    wildcards.append(MySQLWriteCastBase.PLACEHOLDER)
                # COMMENT: avoid MySQLWriteCastBase.resolve when using PLACEHOLDERs
                col_values[-1].append(instances[i][col])

        join_cols = ", ".join(col_names)
        unknown_rows = f'({", ".join(wildcards)})'  # The number of "%s" must match the dict 'dicc_0' length

        self._values = [tuple(x) for x in col_values]
        self._query = f"{self.CLAUSE} {self._model.__table_name__} {f'({join_cols})'} VALUES {unknown_rows}"
        return None

    @staticmethod
    def __is_valid[TProp](column: Column[TProp], value: TProp) -> bool:
        """
        We want to delete the column from table when it's specified with an 'AUTO_INCREMENT' or 'AUTO GENERATED ALWAYS AS (__) STORED' statement.

        if the column is auto-generated, it means the database creates the value for that column, so we must deleted it.
        if the column is primary key and auto-increment, we should be able to create an object with specific pk value.

        RETURN
        -----

        - True  -> Do not delete the column from dict query
        - False -> Delete the column from dict query
        """

        is_pk_none_and_auto_increment: bool = all([value is None, column.is_primary_key, column.is_auto_increment])

        if is_pk_none_and_auto_increment or column.is_auto_generated:
            return False
        return True

    def __fill_dict_list[TProp](self, list_dict: list[str, TProp], values: T | list[T]) -> list[Column]:
        if isinstance(values, Iterable):
            for x in values:
                self.__fill_dict_list(list_dict, x)

        elif issubclass(values.__class__, Table):
            new_list = []
            for prop in type(values).__dict__.values():
                if not isinstance(prop, Column):
                    continue

                value = getattr(values, prop.column_name)
                if self.__is_valid(prop, value):
                    new_list.append(prop)
            list_dict.append(new_list)

        else:
            raise Exception(f"Tipo de dato'{type(values)}' no esperado")
        return None
