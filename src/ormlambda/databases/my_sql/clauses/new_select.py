from typing import override, Type, Callable, TYPE_CHECKING

from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
from ormlambda.common.enums.join_type import JoinType

if TYPE_CHECKING:
    from ormlambda import Table


class Select[T: Type[Table]](DecompositionQueryBase[T]):
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        table: T,
        lambda_query: Callable[[T], tuple] = lambda x: x,
        *,
        alias: bool = False,
        alias_name: str | None = None,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(
            table,
            lambda_query,
            alias=alias,
            alias_name=alias_name,
            by=by,
        )

    # @classmethod
    # def alias_children_resolver[Tclause: Type[Table]](self, clause_info: ClauseInfo[Tclause]):
    #     return f"{clause.table.__table_name__}_{name}"

    @override
    @property
    def query(self) -> str:
        col: str = ", ".join([x.query for x in self.all_clauses])
        query: str = f"{self.CLAUSE} {col} FROM {self._table.__table_name__}"
        alias = ""

        query += alias
        if self.has_foreign_keys:
            query += " " + self.stringify_foreign_key(" ")

        return query
