from collections.abc import Iterable
from typing import override, Any

from orm.utils import Table, Column
from orm.interfaces.IUpsert import AbstractUpsertQuery

from .insert import InsertQuery


class UpsertQuery[T: Table](AbstractUpsertQuery[T], InsertQuery[T]):
    UPSERT = "ON DUPLICATE KEY UPDATE"

    def __init__(self, table: T | list[T]) -> None:
        super().__init__(table)

    @override
    def upsert(self, instances: T | list[T]) -> tuple[str, list[tuple]]:
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
        insert_query, _ = self.insert(instances)

        if isinstance(instances, Table):
            instances = tuple([instances])
        ALIAS = "VALUES"

        cols = instances[0].get_columns()
        pk_key = instances[0].get_pk().column_name

        alternative = ", ".join([f"{col}={ALIAS}({col})" for col in cols if col != pk_key])
        query = f"{insert_query} {self.UPSERT} {alternative};"

        new_dict_list = self.create_dict_list(instances)

        values:list[Any] = []
        for x in new_dict_list:
            values.append(tuple(x.values()))
        return query, values

    @staticmethod
    def is_valid(column: Column) -> bool:
        """
        Eliminamos aquellas columnas autogeneradas y dejamos aquellas columnas unicas para que la consulta falle y realice un upsert

        Aunque una pk sea autogenerada debemos eliminarla de la query ya que no podemos pasar un valor a una columna la cual no acepta valores nuevos.
        Cuando se genere dicha columna y la base de datos detecte que el valor generado está repetido, será entonces cuando detecte la duplicidad y realice ON DUPLICATE KEY UPDATE

        RETURN
        -----

        - True  -> No eliminamos la columna de la consulta
        - False -> Eliminamos la columna
        """
        if (column.is_auto_increment and not column.is_primary_key) or column.is_auto_generated:
            return False
        return True

    def create_dict_list(self, values: T | list[T]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        if isinstance(values, Table):
            dicc: dict = {}
            for col in values.__dict__.values():
                if isinstance(col, Column) and self.is_valid(col):
                    dicc.update({col.column_name: col.column_value})
            result.append(dicc)

        elif isinstance(values, Iterable):
            result: list[dict[str, Any]] = []

            for x in values:
                result.extend(self.create_dict_list(x))
            return result
        return result

    # FIXME [ ]: change interfaces to avoid override 'insert' method
    @override
    def insert(self, instances: T | list[T]):
        return super().insert(instances)
