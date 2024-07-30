from abc import ABC, abstractmethod
from orm.utils import Table
from typing import Any


class IDelete[T](ABC):
    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...


class AbstractDeleteQuery[T: Table](IDelete[T]):
    DELETE = "DELETE"

    def __init__(self, table: Any) -> None:
        if not issubclass(table, Table):
            raise ValueError
        self._table: T | list[T] = table

    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...
