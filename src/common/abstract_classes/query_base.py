from abc import abstractmethod
from src.utils import Table
from src.common.interfaces import IQuery


class QueryBase[T: Table](IQuery):
    @property
    @abstractmethod
    def query(self) -> str: ...
