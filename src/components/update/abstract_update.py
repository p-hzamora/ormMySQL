from abc import abstractmethod
from typing import Any, Optional
from .IUpdate import IUpdate
from src.common.interfaces import IRepositoryBase
from src.common.abstract_classes import NonQueryBase
from src.components.where import AbstractWhere

from src.utils import Table


class UpdateQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IUpdate):
    def __init__(self, model: T, repository: TRepo, where: AbstractWhere = list[AbstractWhere]) -> None:
        super().__init__(model, repository)
        self._where: Optional[AbstractWhere] = where

    @abstractmethod
    def update(self, dicc: dict[str | property, Any]) -> None:
        return super().update(dicc)

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
