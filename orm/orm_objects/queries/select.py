from typing import Callable, overload, Optional, Iterable
import dis

from ..table import Table
from .query import IQuery
from .where_condition import WhereCondition
from orm.dissambler import TreeInstruction


class SelectQuery[T](IQuery):
    @overload
    def __init__(
        self,
        table: Table,
        select_list: Callable[[T], None],
    ) -> None: ...

    @overload
    def __init__(
        self,
        table: Table,
        where: Optional[Callable[[T], None]] = None,
    ) -> None: ...

    def __init__[T2](
        self,
        table: Table,
        select_list: Optional[Callable[[T], None]] = lambda: None,
        where: Optional[Callable[[T, T2], bool]] = None,
    ) -> None:
        self._table:Table = table
        self._where: Optional[WhereCondition[T, T2]] = WhereCondition[T, T2](where) if where else None
        self._select_list: Iterable[str] = self._make_column_list(select_list)

    @staticmethod
    def _make_column_list(select_list: Optional[Callable[[T], None]]) -> Iterable[str]:
        _dis = TreeInstruction(dis.Bytecode(select_list), list).to_list()
        return [x.nested_element.name for x in _dis]

    def _convert_select_list(self) -> str:
        if not self._select_list:
            return "*"
        else:
            select = [f"{self._table.__table_name__}.{col}" for col in self._select_list]
            return ", ".join(select)

    @property
    def query(self) -> str:
        select_str = self._convert_select_list()
        query = f"SELECT {select_str} FROM {self._table.__table_name__}"
        return query
