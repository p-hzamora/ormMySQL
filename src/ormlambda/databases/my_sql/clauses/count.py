import typing as tp

if tp.TYPE_CHECKING:
    from ormlambda import Table
from ormlambda.common.interfaces import IAggregate
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase, ClauseInfo
from ormlambda import JoinType


class Count[T: tp.Type[Table]](DecompositionQueryBase[T], IAggregate[T]):
    NAME: str = "COUNT"

    def __init__(
        self,
        table: T,
        lambda_query: str | tp.Callable[[T], tuple],
        *,
        alias: bool = True,
        alias_name: str = "count",
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(
            table,
            lambda_query=lambda_query,
            alias=alias,
            alias_name=alias_name,
            by=by,
            replace_asterisk_char=False,
        )

    def alias_children_resolver[Tclause: tp.Type[Table]](self, clause_info: ClauseInfo[Tclause]):
        if isinstance(clause_info._row_column, IAggregate):
            return clause_info._row_column.alias
        return None

    @property
    def query(self) -> str:
        col = ", ".join([x.query for x in self.all_clauses])
        return f"{self.NAME}({col})"
