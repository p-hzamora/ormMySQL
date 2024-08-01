from abc import abstractmethod
from typing import Literal
from orm.common.interfaces import IRepositoryBase
from orm.utils import Table

from orm.common.abstract_classes.non_query_base import NonQueryBase

TypeExists = Literal["fail", "replace", "append"]


class DropTableBase[T:Table, TRepo: IRepositoryBase](NonQueryBase[T, TRepo]):
    def __init__(self, model: T, repository: TRepo) -> None:
        super().__init__(model, repository)

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
