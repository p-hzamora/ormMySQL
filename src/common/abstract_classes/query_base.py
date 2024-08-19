from abc import abstractmethod

from ...utils import Table
from ..interfaces import IQuery


class QueryBase[T: Table](IQuery):
    @property
    @abstractmethod
    def query(self) -> str: ...
