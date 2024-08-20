from abc import abstractmethod

from ...common.interfaces import IQuery
from .table_column import TableColumn


class ISelect(IQuery):
    @property
    @abstractmethod
    def select_list(self) -> list[TableColumn]: ...

    @property
    @abstractmethod
    def tables_heritage(self) -> list[TableColumn]: ...
