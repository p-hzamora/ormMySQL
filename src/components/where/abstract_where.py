from abc import abstractmethod
from ...utils import Table

from ...common.interfaces import IQuery


class AbstractWhere(IQuery):
    WHERE: str = "WHERE"

    @abstractmethod
    def get_involved_tables(self) -> tuple[tuple[Table, Table]]: ...
