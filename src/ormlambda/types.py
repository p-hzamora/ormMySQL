import typing as tp

if tp.TYPE_CHECKING:
    from ormlambda import Table, Column



type AsteriskType = str
type TableType[T:Table] = tp.Type[T]
type ColumnType[TProp] = TProp | str | Column | AsteriskType
type AliasType[T] = str | tp.Callable[[T], str]

type ComparerType = tp.Literal["=", "!=", "<", "<=", ">", ">=", "in"]