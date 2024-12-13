from ormlambda.common.interfaces.IAggregate import IAggregate
from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo


import typing as tp
from ormlambda.types import ColumnType
from ormlambda import Column

if tp.TYPE_CHECKING:
    from ormlambda import Table


class Concat[T: tp.Type[Table]](IAggregate):
    FUNCTION_NAME: str = "CONCAT"

    def __init__[*Ts](
        self,
        alias_name: str = "CONCAT",
        *values: ColumnType[Ts],
    ) -> None:
        self._alias_name: str = alias_name
        self._all_clauses: list[ClauseInfo] = []

        for value in values:
            if isinstance(value, Column):
                clause_info = ClauseInfo(value.table, value)
            else:
                clause_info = ClauseInfo(None, value)
            self._all_clauses.append(clause_info)

    @property
    def alias_clause(self) -> tp.Optional[str]:
        return self._alias_name

    @property
    def query(self) -> str:
        string = f"{self.FUNCTION_NAME}({ClauseInfo.join_clauses(self._all_clauses)})"
        return ClauseInfo(IAggregate, string, alias_clause=self._alias_name).query
