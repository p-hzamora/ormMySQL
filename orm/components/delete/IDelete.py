from abc import ABC, abstractmethod


class IDelete[T](ABC):
    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...
