from typing import Any, override

from orm.utils import Table, Column
from orm.components.insert import InsertQueryBase
from orm.common.interfaces import IRepositoryBase
from mysql.connector import MySQLConnection


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
        Validamos si la columna la debemos eliminar o no a la hora de insertar o actualizar valores.

        Querremos elimina un valor de nuestro objeto cuando especifiquemos un valor que en la bbdd sea AUTO_INCREMENT o AUTO GENERATED ALWAYS AS (__) STORED.

        RETURN
        -----

        - True  -> No eliminamos la columna de la consulta
        - False -> Eliminamos la columna
        """
        cond_1 = all([column.column_value is None, column.is_primary_key])
        cond_2 = any([column.is_auto_increment, column.is_auto_generated])

        # not all to get False and deleted column
        return not all([cond_1, cond_2])

    def __fill_dict_list(self, list_dict: list[dict], values: T | list[T]):
        if issubclass(values.__class__, Table):
            dicc: dict = {}
            for col in values.__dict__.values():
                if isinstance(col, Column) and self.__is_valid(col):
                    dicc.update({col.column_name: col.column_value})
            list_dict.append(dicc)
            return list_dict

        elif isinstance(values, list):
            for x in values:
                self.__fill_dict_list(list_dict, x)
        else:
            raise Exception(f"Tipo de dato'{type(values)}' no esperado")
