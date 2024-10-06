from ormlambda.common.interfaces import IAggregate
from ormlambda.databases.my_sql.clauses.decomposition_query import DecompositionQuery


import typing

if typing.TYPE_CHECKING:
    from ormlambda import Table


class Concat(IAggregate):
    CLAUSE = "CONCAT"

    @typing.overload
    def __init__[T](self, table: T, columns: str, *, alias: str = "concat") -> None: ...

    @typing.overload
    def __init__[T: typing.Type[Table], *Ts](self, table: T, columns: typing.Callable[[T], tuple[*Ts]], *, alias: str = "concat") -> None: ...

    def __init__[T: typing.Type[Table], *Ts](self, table: T, column: str | typing.Callable[[T], tuple[*Ts]] = "*", *, alias: str = "concat") -> None:
        self._table: T = table
        self._column: str | typing.Callable[[T], typing.Any] = column
        self._alias: str = alias

    @property
    def query(self) -> str:
        decom = DecompositionQuery(self._table, self._column, alias=False)
        col = decom.query

        return f"{self.CLAUSE}({col}) as `{self._alias}`"
