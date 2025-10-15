from typing import TYPE_CHECKING, Literal, Callable, Type, Union


if TYPE_CHECKING:
    from ormlambda.sql.functions.interface import IFunction
    from ormlambda import Table
    from ormlambda.sql.comparer import Comparer
    from ormlambda.common.enums import JoinType
    from ormlambda.common.enums import UnionEnum
    from ormlambda import ColumnProxy, TableProxy


type TableType[T: Table] = Type[T] | TableProxy[T]
type ColumnType[TProp] = TProp | ColumnProxy[TProp]
type AliasType[TProp] = str | Callable[[ColumnProxy[TProp]], str]

# region Comparer Types
type ComparerType = Union[
    Literal["=", "!=", "<", "<=", ">", ">=", "in"],
    str,
]
type ConditionType[TProp] = Comparer | ColumnType[TProp]
type UnionType = Literal["AND", "OR"] | UnionEnum
type SelectCol = ColumnProxy | IFunction | Comparer
type JoinType = JoinType
# endregion

type TupleJoinType[T] = tuple[Comparer]

ASTERISK = "*"

type compileOptions = Literal[
    "select",
    "where",
    "having",
    "order",
    "group_by",
    "limit",
    "offset",
    # "joins",
    "count",
]
# TODOL []: Look if we can avoid this *
from .compiler import *  # noqa: F403, E402
