from typing import override, Callable, overload, Iterable, Optional
import dis
from abc import abstractmethod

from ...interfaces.IQuery import IQuery
from ..table import Table
from .where_condition import WhereCondition
from orm.dissambler import TreeInstruction


class QuerySelector[T](IQuery):
    @overload
    def __init__(
        self,
        orig_table: Table,
    ) -> None: ...

    @overload
    def __init__(
        self,
        where: WhereCondition,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
        where: WhereCondition,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
        select_list: Callable[[T], None],
    ) -> None: ...

    @overload
    def __init__(
        self,
        orig_table: Table,
        select_list: Iterable[Callable[[T], None]],
    ) -> None: ...

    def __init__[T2](
        self,
        orig_table: Table,
        select_list: Optional[Callable[[T], None] | Iterable[Callable[[T], None]]] = None,
        where: Optional[Callable[[T, T2], bool] | Iterable[Callable[[T, T2], bool]]] = None,
    ) -> None:
        _dis = TreeInstruction(dis.Bytecode(select_list), "list").to_list()
        self._select_list: Optional[Callable[[T], None] | Iterable[Callable[[T], None]]] = [x.nested_element.name for x in _dis]
        self._select_str: str = self._convert_select_list(self._select_list)
        self._orig_table: Table = orig_table
        self._where: WhereCondition = WhereCondition[T, T2](where) if where else None

    def _convert_select_list(self, select_list: Callable[[T], None] | Iterable[Callable[[T], None]]) -> str:
        if select_list is None:
            return "*"
        else:
            return ", ".join(select_list)

    @property
    @abstractmethod
    def query(self) -> str: ...

    @override
    def load(self) -> str:
        condition = ""
        if self._where:
            condition = " " + self._where.to_query()
        return f"{self.query}{condition}{self.SEMICOLON}"
