from __future__ import annotations
from typing import Callable, Iterable, Optional, Literal, Union, TYPE_CHECKING
import enum


from ormlambda.common.enums import JoinType

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer

type OrderTypes = Literal["ASC", "DESC"] | OrderType | Iterable[OrderType]


class OrderType(enum.Enum):
    ASC = "ASC"
    DESC = "DESC"


type Tuple[T] = tuple[T, ...]

type SelectRes1[T1] = tuple[Tuple[T1]]
type SelectRes2[T1, T2] = tuple[*SelectRes1[T1], Tuple[T2]]
type SelectRes3[T1, T2, T3] = tuple[*SelectRes2[T1, T2], Tuple[T3]]
type SelectRes4[T1, T2, T3, T4] = tuple[*SelectRes3[T1, T2, T3], Tuple[T4]]
type SelectRes5[T1, T2, T3, T4, T5] = tuple[*SelectRes4[T1, T2, T3, T4], Tuple[T5]]
type SelectRes6[T1, T2, T3, T4, T5, T6] = tuple[*SelectRes5[T1, T2, T3, T4, T5], Tuple[T6]]
type SelectRes7[T1, T2, T3, T4, T5, T6, T7] = tuple[*SelectRes6[T1, T2, T3, T4, T5, T6], Tuple[T7]]
type SelectRes8[T1, T2, T3, T4, T5, T6, T7, T8] = tuple[*SelectRes7[T1, T2, T3, T4, T5, T6, T7], Tuple[T8]]
type SelectRes9[T1, T2, T3, T4, T5, T6, T7, T8, T9] = tuple[*SelectRes8[T1, T2, T3, T4, T5, T6, T7, T8], Tuple[T9]]
type SelectRes10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10] = tuple[*SelectRes9[T1, T2, T3, T4, T5, T6, T7, T8, T9], Tuple[T10]]

type WhereCondition[T, T1] = Callable[[T, T1], bool]
type JoinCondition[T, T1] = tuple[T1, WhereCondition[T, T1], Optional[JoinType]]

type TupleJoins1[T, T1] = tuple[JoinCondition[T, T1]]
type TupleJoins2[T, T1, T2] = tuple[*TupleJoins1[T, T1], JoinCondition[T, T2]]
type TupleJoins3[T, T1, T2, T3] = tuple[*TupleJoins2[T, T1, T2], JoinCondition[T, T3]]
type TupleJoins4[T, T1, T2, T3, T4] = tuple[*TupleJoins3[T, T1, T2, T3], JoinCondition[T, T4]]
type TupleJoins5[T, T1, T2, T3, T4, T5] = tuple[*TupleJoins4[T, T1, T2, T3, T4], JoinCondition[T, T5]]
type TupleJoins6[T, T1, T2, T3, T4, T5, T6] = tuple[*TupleJoins5[T, T1, T2, T3, T4, T5], JoinCondition[T, T6]]


# TODOH: This var is duplicated from 'src\ormlambda\databases\my_sql\clauses\create_database.py'
type TypeExists = Literal["fail", "replace", "append"]


type WhereTypes[LTable, LProp, RTable, RProp] = Union[
    bool,
    Comparer[LTable, LProp, RTable, RProp],
    tuple[Comparer[LTable, LProp, RTable, RProp], ...],
    Callable[[LTable], WhereTypes[LTable, LProp, RTable, RProp]],
]
