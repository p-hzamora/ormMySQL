from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Table, IRepositoryBase
from ormlambda.common.abstract_classes import NonQueryBase

from .IDelete import IDelete


class DeleteQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IDelete[T]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @abstractmethod
    def delete(self, instances: T | list[T]) -> None: ...
