from abc import abstractmethod
from src.utils import Table

from src.common.interfaces import IQuery


class AbstractWhere(IQuery):
    WHERE: str = "WHERE"

    @abstractmethod
    def get_involved_tables(self) -> tuple[tuple[Table, Table]]: ...
