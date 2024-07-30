from abc import ABC, abstractmethod
from orm.utils import Table


class IUpsert[T](ABC):
    @abstractmethod
    def upsert(self, instances: T | list[T]): ...


class AbstractUpsertQuery[T: Table](IUpsert[T]):
    def __init__(self, table: T | list[T]) -> None:
        super().__init__(table)
