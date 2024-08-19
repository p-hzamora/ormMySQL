from src.utils import Table
from abc import abstractmethod

from src.common.interfaces import IRepositoryBase
from src.common.abstract_classes import NonQueryBase

from .IDelete import IDelete


class DeleteQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IDelete[T]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...
