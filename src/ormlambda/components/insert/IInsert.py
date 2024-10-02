from abc import ABC, abstractmethod


class IInsert[T](ABC):
    @abstractmethod
    def insert(self, instances: T | list[T]) -> None: ...
