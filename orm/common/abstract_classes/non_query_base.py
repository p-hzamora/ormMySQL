from abc import abstractmethod
from typing import Any, Optional, override
from orm.common.interfaces.INonQueryCommand import INonQueryCommand

from orm.common.interfaces import IRepositoryBase
from orm.utils import Table


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
