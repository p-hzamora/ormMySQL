import typing as tp

from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import ClauseInfo


type ConcatResponse[TProp] = tuple[str | ColumnType[TProp]]


class Concat[T](AggregateFunctionBase[T]):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "CONCAT"

    def __init__[TProp](
        self,
        values: ConcatResponse[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = "concat",
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            table=None,
            column=values,
            alias_clause=alias_clause,
            context=context,
            dtype=str,
        )

    @tp.override
    @property
    def query(self) -> str:
        columns: list[str] = []

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None

        for clause in self._convert_into_clauseInfo(self.unresolved_column, context=context):
            clause.alias_clause = self.alias_clause
            columns.append(clause)
        return self._concat_alias_and_column(f"{self.FUNCTION_NAME()}({ClauseInfo.join_clauses(columns)})", self._alias_aggregate)
