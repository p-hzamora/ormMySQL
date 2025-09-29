from typing import TYPE_CHECKING, Literal, Callable, Type


if TYPE_CHECKING:
    from ormlambda.sql.clause_info import IAggregate
    from ormlambda import Table
    from ormlambda.sql.comparer import Comparer
    from ormlambda import ConditionType as ConditionEnum
    from ormlambda.common.enums.join_type import JoinType as JoinType
    from ormlambda.sql.column import ColumnProxy


type TableType[T: Table] = Type[T]
type ColumnType[TProp] = TProp | ColumnProxy[TProp]
type AliasType[TProp] = str | Callable[[ColumnProxy[TProp]], str]

# region Comparer Types
type ComparerType = Literal["=", "!=", "<", "<=", ">", ">=", "in"]
type ConditionType[TProp] = Comparer | ColumnType[TProp]
type UnionType = Literal["AND", "OR", ""]
type ComparerTypes = ComparerType | UnionType | ConditionEnum
type SelectCol = ColumnProxy | IAggregate | Comparer
# endregion

type TupleJoinType[T] = tuple[Comparer]

ASTERISK = "*"

# TODOL []: Look if we can avoid this * 
from .compiler import *  # noqa: F403, E402
