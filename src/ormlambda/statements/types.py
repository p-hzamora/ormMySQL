from __future__ import annotations
from typing import (
    Callable,
    Iterable,
    Optional,
    Literal,
    Union,
    TYPE_CHECKING,
)


if TYPE_CHECKING:
    from ormlambda.common.enums import JoinType
    from ormlambda.sql.comparer import Comparer
    from ormlambda.sql.types import ColumnType
    from ormlambda.common.enums import OrderType

type OrderTypes = Literal["ASC", "DESC"] | OrderType | Iterable[OrderType]


type Tuple[*T] = tuple[tuple[*T], ...]
type WhereCondition[T, T1] = Callable[[T, T1], bool]
type JoinCondition[T, T1] = tuple[T1, WhereCondition[T, T1], Optional[JoinType]]


type TypeExists = Literal["fail", "replace", "append"]


type WhereTypes[LTable] = Union[
    bool,
    Comparer,
    Callable[[LTable], WhereTypes[LTable]],
    Iterable[WhereTypes[LTable]],
]


type SelectCols[T, TProp] = Callable[[T], ColumnType[TProp]] | ColumnType[TProp]
