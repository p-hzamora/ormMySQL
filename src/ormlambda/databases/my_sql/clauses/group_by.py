import typing as tp
from ormlambda.common.enums.join_type import JoinType
from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo, DecompositionQueryBase
from ormlambda.common.interfaces.IAggregate import IAggregate
from ormlambda import Table


class GroupBy[T: tp.Type[Table], *Ts, TProp](DecompositionQueryBase[T], IAggregate[T]):
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
            lambda_query=column,
            alias=alias,
            alias_name=alias_name,
            by=by,
        )

    def alias_children_resolver[Tclause: tp.Type[Table]](self, clause_info: ClauseInfo[Tclause]):
        return None

    @property
    def query(self) -> str:
        col: str = ", ".join([x.query for x in self.all_clauses])

        return f"{self.CLAUSE} {col}"
