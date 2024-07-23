from typing import Callable, Any, Optional, Literal
from abc import abstractmethod, ABC
from enum import Enum
from collections import defaultdict

from orm.utils import Table
from orm.interfaces import IQuery

OrderType = Literal["ASC", "DESC"]


class JoinType(Enum):
    RIGHT_INCLUSIVE = "RIGHT JOIN"
    LEFT_INCLUSIVE = "LEFT JOIN"
    RIGHT_EXCLUSIVE = "RIGHT JOIN"
    LEFT_EXCLUSIVE = "LEFT JOIN"
    FULL_OUTER_INCLUSIVE = "RIGHT JOIN"
    FULL_OUTER_EXCLUSIVE = "RIGHT JOIN"
    INNER_JOIN = "INNER JOIN"


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "with_recursive", "limit", "offset"]


class AbstractSQLStatements[T](ABC):
    __order__: tuple[ORDER_QUERIES] = ("select", "join", "where", "order", "with", "with_recursive", "limit", "offset")

    def __init__(self) -> None:
        self._query: dict[ORDER_QUERIES, list[IQuery]] = defaultdict(list)

    @abstractmethod
    def where(self, instance: tuple[Table], lambda_: Callable[[T], bool], **kwargs: dict[str, Any]) -> "AbstractSQLStatements": ...

    @abstractmethod
    def join(self, table_left: Table, table_right: Table, *, by: str) -> "AbstractSQLStatements": ...

    @abstractmethod
    def select[*Ts](self, tables: tuple[T, *Ts], selector: Optional[Callable[[T, *Ts], None]] = lambda: None, by: JoinType = JoinType.INNER_JOIN) -> "AbstractSQLStatements": ...

    @abstractmethod
    def order(self, instance: T, _lambda_col: Callable[[T], None], order_type: OrderType) -> "AbstractSQLStatements": ...

    @abstractmethod
    def build(self) -> "AbstractSQLStatements": ...

    @abstractmethod
    def limit(self, number: int) -> "AbstractSQLStatements": ...

    @abstractmethod
    def offset(self, number: int) -> "AbstractSQLStatements": ...
