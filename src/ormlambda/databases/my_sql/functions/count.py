from typing import Any, Callable, Type, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Table
from ormlambda.common.interfaces import IAggregate
from ormlambda.databases.my_sql.clauses.decomposition_query import DecompositionQuery


class Count(IAggregate):
    NAME: str = "COUNT"

    @overload
    def __init__[T: Type[Table]](self, table: T, column: str, *, alias: str = "count") -> None: ...
    @overload
    def __init__[T: Type[Table]](self, table: T, column: Callable[[T], Any], *, alias: str = "count") -> None: ...

    def __init__[T: Type[Table]](self, table: T, column: str | Callable[[T], Any] = "*", *, alias: str = "count") -> None:
        self._table: T = table
        self._column: DecompositionQuery | str | Callable[[T], Any] = column
        self._alias: str = alias

    @property
    def query(self) -> str:
        decom = DecompositionQuery(self._table, self._column, alias=False)
        col = decom.query

        return f"{self.NAME}({col}) as `{self._alias}`"
