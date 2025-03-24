import typing as tp


if tp.TYPE_CHECKING:
    from ormlambda import Table, Column, ForeignKey
    from ormlambda.sql.comparer import Comparer
    from ormlambda import ConditionType as ConditionEnum
    from ormlambda.common.enums.join_type import JoinType


type AsteriskType = str
type TableType[T: Table] = tp.Type[T] | ForeignKey[T]
type ColumnType[TProp] = TProp | Column[TProp] | AsteriskType | tuple[Column]
type AliasType[T] = tp.Optional[str | tp.Callable[[T], str]]

# region Comparer Types
type ComparerType = tp.Literal["=", "!=", "<", "<=", ">", ">=", "in"]
type ConditionType[TProp] = Comparer | ColumnType[TProp]
type UnionType = tp.Literal["AND", "OR", ""]
type ComparerTypes = ComparerType | UnionType | ConditionEnum
# endregion

type TupleJoinType[T] = tuple[Comparer[T], JoinType]

ASTERISK: AsteriskType = "*"
