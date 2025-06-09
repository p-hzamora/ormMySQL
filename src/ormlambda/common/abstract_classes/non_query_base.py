from __future__ import annotations
from abc import abstractmethod
from typing import Any, Optional, Type, TYPE_CHECKING

from ormlambda.common.interfaces.INonQueryCommand import INonQueryCommand

if TYPE_CHECKING:
    from ormlambda.repository import BaseRepository
    from ormlambda.dialects import Dialect
    from ormlambda import Table
    from ormlambda.engine import Engine


class NonQueryBase[T: Type[Table], TRepo](INonQueryCommand):
    __slots__: tuple[str, ...] = ("_model", "_repository", "_values", "_query")

    def __init__(self, model: T, repository: TRepo, **kwargs) -> None:
        self._model: T = model
        self._repository: BaseRepository[TRepo] = repository
        self._values: list[tuple[Any]] = []
        self._query: Optional[str] = None
        self._dialect: Dialect = kwargs.get("dialect", None)
        self._engine: Optional[Engine] = kwargs.get("engine", None)

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...

    def query(self, dialect: Dialect, **kwargs) -> str:
        return self._query

    @property
    def values(self) -> list[tuple[Any, ...]]:
        return self._values
