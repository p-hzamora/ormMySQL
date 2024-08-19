from abc import abstractmethod
from typing import Any, Optional, override

from ..interfaces.INonQueryCommand import INonQueryCommand

from ..interfaces import IRepositoryBase
from ...utils import Table


class NonQueryBase[T: Table, TRepo: IRepositoryBase](INonQueryCommand):
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
