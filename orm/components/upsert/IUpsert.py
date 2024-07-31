from abc import ABC, abstractmethod


class IUpsert[T](ABC):
    @abstractmethod
    def upsert(self, instances: T | list[T]) -> None: ...
