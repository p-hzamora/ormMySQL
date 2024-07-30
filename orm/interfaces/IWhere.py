from abc import abstractmethod
from orm.utils import Table

from orm.interfaces import IQuery


class AbstractWhere(IQuery):
    WHERE: str = "WHERE"

    @abstractmethod
    def get_involved_tables(self) -> tuple[tuple[Table, Table]]: ...

