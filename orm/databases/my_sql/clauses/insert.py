from typing import Any, override

from orm.utils import Table, Column
from orm.interfaces.IInsert import AbstractInsertQuery


class InsertQuery[T: Table](AbstractInsertQuery[T]):
    def __init__(self, table: T | list[T]) -> None:
        super().__init__(table)

    @override
    def insert(self, instances: T | list[T]) -> tuple[str, list[tuple]]:
        new_dict_list: list[dict[str, Any]] = self.__fill_dict_list(instances)
        cols_tuple = new_dict_list[0].keys()
        join_cols = ", ".join(cols_tuple)
        unknown_rows = f'({", ".join(["%s"]*len(cols_tuple))})'  # The number of "%s" must match the dict 'dicc_0' length

        values = [tuple(x.values()) for x in new_dict_list]
        return f"{self.INSERT} {self._table.__table_name__} {f'({join_cols})'} VALUES {unknown_rows}", values

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

    def __fill_dict_list(self, values: T | list[T]):
        if issubclass(values.__class__, Table):
            new_dict_list = []
            dicc: dict = {}
            for col in values.__dict__.values():
                if isinstance(col, Column) and self.__is_valid(col):
                    dicc.update({col.column_name: col.column_value})
            new_dict_list.append(dicc)
            return new_dict_list

        elif isinstance(values, list):
            for x in values:
                self.__fill_dict_list(new_dict_list, x)
        else:
            raise Exception(f"Tipo de dato'{type(values)}' no esperado")
