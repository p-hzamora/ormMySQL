from __future__ import annotations
from typing import (
    Callable,
    Iterable,
    Optional,
    Literal,
    Union,
    TYPE_CHECKING,
)
import enum


from ormlambda.common.enums import JoinType

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer

type OrderTypes = Literal["ASC", "DESC"] | OrderType | Iterable[OrderType]


class OrderType(enum.Enum):
    ASC = "ASC"
    DESC = "DESC"


type Tuple[T] = tuple[T, ...]

type Select2[T1, T2] = tuple[Tuple[T1], Tuple[T2]]
type Select3[T1, T2, T3] = tuple[*Select2[T1, T2], Tuple[T3]]
type Select4[T1, T2, T3, T4] = tuple[*Select3[T1, T2, T3], Tuple[T4]]
type Select5[T1, T2, T3, T4, T5] = tuple[*Select4[T1, T2, T3, T4], Tuple[T5]]
type Select6[T1, T2, T3, T4, T5, T6] = tuple[*Select5[T1, T2, T3, T4, T5], Tuple[T6]]
type Select7[T1, T2, T3, T4, T5, T6, T7] = tuple[*Select6[T1, T2, T3, T4, T5, T6], Tuple[T7]]
type Select8[T1, T2, T3, T4, T5, T6, T7, T8] = tuple[*Select7[T1, T2, T3, T4, T5, T6, T7], Tuple[T8]]
type Select9[T1, T2, T3, T4, T5, T6, T7, T8, T9] = tuple[*Select8[T1, T2, T3, T4, T5, T6, T7, T8], Tuple[T9]]
type Select10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10] = tuple[*Select9[T1, T2, T3, T4, T5, T6, T7, T8, T9], Tuple[T10]]

type WhereCondition[T, T1] = Callable[[T, T1], bool]
type JoinCondition[T, T1] = tuple[T1, WhereCondition[T, T1], Optional[JoinType]]


# TODOH [x]: This var is duplicated from 'src\ormlambda\databases\my_sql\clauses\create_database.py'
type TypeExists = Literal["fail", "replace", "append"]


type WhereTypes[LTable, LProp, RTable, RProp] = Union[
    bool,
    Comparer[LTable, LProp, RTable, RProp],
    tuple[Comparer[LTable, LProp, RTable, RProp], ...],
    Callable[[LTable], WhereTypes[LTable, LProp, RTable, RProp]],
]
