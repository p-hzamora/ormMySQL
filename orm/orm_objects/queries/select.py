from typing import Callable, Optional, Iterable
import dis

from .query import IQuery
from orm.dissambler import TreeInstruction


class SelectQuery[T](IQuery):
    def __init__(
        self,
        table: T,
        select_list: Optional[Callable[..., None]] = lambda: None,
    ) -> None:
        self._table: tuple[T] = table
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
