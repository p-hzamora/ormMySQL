from abc import abstractmethod
from orm.utils import Table
from orm.common.interfaces import IQuery


class QueryBase[T:Table](IQuery):
    @property
    @abstractmethod
    def query(self) -> str: ...
