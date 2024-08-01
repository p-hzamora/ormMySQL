from abc import abstractmethod
from typing import Literal
from orm.common.interfaces import IRepositoryBase

from orm.common.abstract_classes.non_query_base import NonQueryBase

TypeExists = Literal["fail", "replace", "append"]


class CreateDatabaseBase[TRepo: IRepositoryBase](NonQueryBase[None, TRepo]):
    def __init__(self, repository: TRepo) -> None:
        super().__init__(None, repository)

    @property
    @abstractmethod
    def CLAUSE(self) -> str: ...

    @abstractmethod
    def execute(self, name: str, if_exists: TypeExists = "fail") -> None: ...
