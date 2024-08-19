from abc import abstractmethod

from .IDelete import IDelete
from ...utils import Table
from ...common.interfaces import IRepositoryBase
from ...common.abstract_classes import NonQueryBase


class DeleteQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IDelete[T]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...
