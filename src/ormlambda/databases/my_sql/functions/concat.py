from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


import typing as tp
from ormlambda.types import ColumnType, AliasType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo


class Concat[*Ts](AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "CONCAT"

    def __init__[TProp](
        self,
        values: ColumnType[Ts] | tuple[ColumnType[Ts], ...],
        alias_clause: AliasType[ColumnType[TProp]] = "concat",
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        super().__init__(
            column=values,
            alias_clause=alias_clause,
            context=context,
        )

    @tp.override
    @property
    def query(self) -> str:
        columns: list[str] = []

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None)
        for clause in self._convert_into_clauseInfo(self.unresolved_column, context):
            new_clause = clause
            new_clause.alias_clause = None
            columns.append(new_clause)
        return f"{self.FUNCTION_NAME()}({ClauseInfo.join_clauses(columns)})"
