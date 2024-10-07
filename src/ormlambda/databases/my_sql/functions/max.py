from ormlambda.common.interfaces import IAggregate
import typing as tp

from ormlambda.databases.my_sql.clauses.decomposition_query import DecompositionQuery

if tp.TYPE_CHECKING:
    from ormlambda import Table


class Max(IAggregate):
    NAME: str = "MAX"

    @tp.overload
    def __init__[T: tp.Type[Table]](self, table: T, column: str, *, alias: str = "maximun") -> None: ...
    @tp.overload
    def __init__[T: tp.Type[Table]](self, table: T, column: tp.Callable[[T], tp.Any], *, alias: str = "maximun") -> None: ...

    def __init__[T: tp.Type[Table]](self, table: T, column: str | tp.Callable[[T], tp.Any] = "*", *, alias: str = "maximun") -> None:
        self._table: T = table
        self._column: DecompositionQuery | str | tp.Callable[[T], tp.Any] = column
        self._alias: str = alias

    @property
    def query(self) -> str:
        decom = DecompositionQuery(self._table, self._column, alias=False)
        col = decom.query

        return f"{self.NAME}({col}) as `{self._alias}`"
