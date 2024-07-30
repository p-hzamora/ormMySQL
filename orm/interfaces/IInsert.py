from abc import ABC, abstractmethod
from orm.utils import Table


class IInsert[T](ABC):
    @abstractmethod
    def insert(self, instances: T | list[T]): ...


class AbstractInsertQuery[T: Table](IInsert[T]):
    INSERT: str = "INSERT INTO"

    def __init__(self, table: T | list[T]) -> None:
        self._table: T = table
