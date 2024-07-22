from typing import Callable, Any, Optional, Literal
from abc import abstractmethod, ABC
from enum import Enum

from ..orm_objects.table import Table
from .IQuery import IQuery

OrderType = Literal["ASC", "DESC"]


class JoinType(Enum):
    RIGHT_INCLUSIVE = "RIGHT JOIN"
    LEFT_INCLUSIVE = "LEFT JOIN"
    RIGHT_EXCLUSIVE = "RIGHT JOIN"
    LEFT_EXCLUSIVE = "LEFT JOIN"
    FULL_OUTER_INCLUSIVE = "RIGHT JOIN"
    FULL_OUTER_EXCLUSIVE = "RIGHT JOIN"
    INNER_JOIN = "INNER JOIN"


class ISQLStatements[T](ABC):
    @abstractmethod
    def where(self, instance: tuple[Table], lambda_: Callable[[T], bool], **kwargs: dict[str, Any]) -> IQuery: ...

    @abstractmethod
    def join(self, table_left: Table, table_right: Table, *, by: str) -> IQuery: ...

    @abstractmethod
    def select[*Ts](self, tables: tuple[T, *Ts], selector: Optional[Callable[[T, *Ts], None]] = lambda: None, by: JoinType = JoinType.INNER_JOIN) -> IQuery: ...

    @abstractmethod
    def order(self, instance: T, _lambda_col: Callable[[T], None], order_type: OrderType) -> IQuery: ...

    @abstractmethod
    def build(self) -> IQuery: ...

    @abstractmethod
    def limit(self, number: int) -> IQuery: ...

    @abstractmethod
    def offset(self, number: int) -> IQuery: ...
