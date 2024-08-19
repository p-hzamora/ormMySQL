from abc import abstractmethod
from .IUpsert import IUpsert
from src.common.interfaces import IRepositoryBase
from src.common.abstract_classes import NonQueryBase

from src.utils import Table


class UpsertQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IUpsert[T]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @abstractmethod
    def upsert(self, instances: T | list[T]) -> None: ...

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
