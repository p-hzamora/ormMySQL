from typing import Any, override, Iterable

from orm.utils import Table, Column
from orm.interfaces.IDelete import AbstractDeleteQuery


class DeleteQuery[T: Table](AbstractDeleteQuery[T]):
    def __init__(self, table: list[T] | T) -> None:
        super().__init__(table)

    @override
    def delete(self, instances: T | list[T]) -> None:
        col: str = ""
        if isinstance(instances, Table):
            pk: Column = instances.get_pk()
            if pk.column_value is None:
                raise Exception(f"You cannot use 'DELETE' query without set primary key in '{instances.__table_name__}'")
            col = pk.column_name
            value = str(pk.column_value)

        elif isinstance(instances, Iterable):
            value: list[Any] = []
            for ins in instances:
                pk = ins.get_pk()
                col = pk.column_name
                value.append(pk.column_value)

        query: str = f"{self.DELETE} FROM {self._table.__table_name__} WHERE {col}"
        if isinstance(value, str):
            query += "= %s"
            return query, [value]
        elif isinstance(value, Iterable):
            params = ", ".join(["%s"] * len(value))
            query += f" IN ({params})"
            return query, value
        else:
            raise Exception(f"'{type(value)}' no esperado")
        return None
