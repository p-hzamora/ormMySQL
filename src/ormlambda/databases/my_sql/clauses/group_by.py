import typing as tp
from ormlambda.common.enums.join_type import JoinType
from ormlambda.sql.clause_info import IAggregate
from ormlambda import Table
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase


class GroupBy[T: tp.Type[Table], *Ts, TProp](DecompositionQueryBase[T], IAggregate):
    CLAUSE: str = "GROUP BY"

    def __init__(
        self,
        table: T,
        column: tp.Callable[[T, *Ts], TProp],
        *,
        alias: bool = True,
        alias_name: str | None = None,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(
            table,
            columns=column,
            alias=alias,
            alias_name=alias_name,
            by=by,
        )

    @property
    def query(self) -> str:
        col: str = ", ".join([x.query for x in self.all_clauses])

        return f"{self.CLAUSE} {col}"
