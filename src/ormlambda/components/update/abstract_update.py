from __future__ import annotations
from abc import abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from ormlambda.common.abstract_classes import NonQueryBase
from ormlambda.databases.my_sql.clauses.where import Where

if TYPE_CHECKING:
    from ormlambda.repository import IRepositoryBase
    from ormlambda import Table

from .IUpdate import IUpdate


class UpdateQueryBase[T: Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo], IUpdate):
    def __init__(self, model: T, repository: TRepo, where: list[Where] = list[Where]) -> None:
        super().__init__(model, repository)
        self._where: Optional[list[Where]] = where

    @abstractmethod
    def update(self, dicc: dict[str | property, Any]) -> None:
        return super().update(dicc)

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
