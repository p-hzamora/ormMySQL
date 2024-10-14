from ormlambda.common.interfaces.IAggregate import IAggregate
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase, ClauseInfo


import typing as tp
from ormlambda.common.enums.join_type import JoinType

if tp.TYPE_CHECKING:
    from ormlambda import Table


class Concat[T: tp.Type[Table]](DecompositionQueryBase[T], IAggregate[T]):
    CLAUSE = "CONCAT"

    def __init__[*Ts](
        self,
        table: T,
        lambda_query: str | tp.Callable[[T], tuple[*Ts]],
        *,
        alias: bool = True,
        alias_name: str = "CONCAT",
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(
            table,
            lambda_query,
            alias=alias,
            alias_name=alias_name,
            by=by,
        )

    def alias_children_resolver[Tclause: tp.Type[Table]](self, clause_info: ClauseInfo[Tclause]):
        if isinstance(clause_info._row_column, IAggregate):
            return clause_info._row_column.alias
        return None

    @property
    def query(self) -> str:
        col: str = ", ".join([x.query for x in self.all_clauses])

        return f"{self.CLAUSE}({col})"
