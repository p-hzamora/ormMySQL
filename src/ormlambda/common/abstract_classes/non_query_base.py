from __future__ import annotations
from abc import abstractmethod
from typing import Any, Optional, Type, override, TYPE_CHECKING

from ormlambda.common.interfaces.INonQueryCommand import INonQueryCommand

if TYPE_CHECKING:
    from ormlambda import IRepositoryBase
    from ormlambda import Table


class NonQueryBase[T: Type[Table], TRepo: IRepositoryBase](INonQueryCommand):
    __slots__: tuple[str, ...] = ("_model", "_repository", "_values", "_query")

    def __init__(self, model: T, repository: TRepo) -> None:
        self._model: T = model
        self._repository: TRepo = repository
        self._values: list[tuple[Any]] = []
        self._query: Optional[str] = None

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...

    @property
    @override
    def query(self) -> str:
        return self._query

    @property
    def values(self) -> list[tuple[Any, ...]]:
        return self._values
