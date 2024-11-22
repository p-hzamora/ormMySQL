from ormlambda.common.interfaces import IAggregate
import typing as tp

from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase

if tp.TYPE_CHECKING:
    from ormlambda import Table


class Sum[T: tp.Type[Table]](DecompositionQueryBase[T], IAggregate[T]):
    NAME: str = "SUM"

    @tp.overload
    def __init__[T: tp.Type[Table]](self, table: T, column: tp.Callable[[T], tp.Any], *, alias: bool = True, alias_name: str = ...) -> None: ...

    def __init__(
        self,
        table: T,
        column: str | tp.Callable[[T], tuple],
        *,
        alias: bool = True,
        alias_name: str = "sum",
    ) -> None:
        super().__init__(
            table,
            lambda_query=column,
            alias=alias,
            alias_name=alias_name,
        )

    @property
    def query(self) -> str:
        col = ", ".join([x.query for x in self.all_clauses])
        return f"{self.NAME}({col})"
