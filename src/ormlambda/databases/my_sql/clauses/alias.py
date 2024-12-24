import typing as tp
from ormlambda import Table
from ormlambda.common.interfaces import ICustomAlias

from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ..mysql_decomposition import MySQLDecompositionQuery


class Alias[T: tp.Type[Table], *Ts](MySQLDecompositionQuery[T, *Ts], ICustomAlias[T, *Ts]):
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
            columns=query,
            alias=alias,
            alias_name=alias_name,
        )

    @property
    def query(self) -> str:
        assert len(self.all_clauses) == 1

        return self.all_clauses[0].query
