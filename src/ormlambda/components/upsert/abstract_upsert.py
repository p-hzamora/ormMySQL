from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import IRepositoryBase
    from ormlambda import Table

from ormlambda.common.abstract_classes import NonQueryBase
from .IUpsert import IUpsert


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
