import typing as tp

if tp.TYPE_CHECKING:
    from ormlambda import Table, Column
    from ormlambda.common.abstract_classes.comparer import Comparer


type AsteriskType = str
type TableType[T: Table] = tp.Type[T]
type ColumnType[TProp] = TProp | Column[TProp] | AsteriskType
type AliasType[T] = tp.Optional[str | tp.Callable[[T], str]]

type ComparerType = tp.Literal["=", "!=", "<", "<=", ">", ">=", "in"]


type TupleJoinType[T] = tuple[str, T, Comparer[T]]
