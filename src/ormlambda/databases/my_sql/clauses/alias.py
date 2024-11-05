import typing as tp
from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo, DecompositionQueryBase
from ormlambda import Table

from ormlambda.common.interfaces import ICustomAlias


class Alias[T: tp.Type[Table], *Ts](DecompositionQueryBase[T, *Ts], ICustomAlias[T, *Ts]):
    def __init__(
        self,
        table: T,
        query: tp.Callable[[T, *Ts], tp.Any],
        *,
        alias: bool = True,
        alias_name: str | None = None,
    ) -> None:
        super().__init__(
            table,
            lambda_query=query,
            alias=alias,
            alias_name=alias_name,
        )

    def alias_children_resolver[Tclause: tp.Type[Table]](self, clause_info: ClauseInfo[Tclause]):
        return self.alias_name

    @property
    def query(self) -> str:
        assert len(self.all_clauses) == 1

        return self.all_clauses[0].query
