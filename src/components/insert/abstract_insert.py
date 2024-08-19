from abc import abstractmethod
from ...utils import Table

from .IInsert import IInsert
from ...common.interfaces import IRepositoryBase
from ...common.abstract_classes import NonQueryBase


class InsertQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, IRepositoryBase], IInsert[T]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @abstractmethod
    def insert(self, instances: T | list[T]) -> None: ...

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
