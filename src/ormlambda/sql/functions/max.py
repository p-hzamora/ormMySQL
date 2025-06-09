from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import AggregateFunctionBase

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Max(AggregateFunctionBase[None]):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "MAX"

    def __init__[TProp](
        self,
        elements: ColumnType[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = "max",
        context: ClauseContextType = None,
        *,
        dialect: Dialect,
    ):
        super().__init__(
            table=None,
            column=elements,
            alias_table=None,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=False,
            preserve_context=False,
            dialect=dialect,
        )

    @tp.override
    def query(self, dialect: Dialect, **kwargs) -> str:
        columns: list[str] = []

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None
        for clause in self._convert_into_clauseInfo(self.unresolved_column, context, dialect=self._dialect):
            new_clause = clause
            new_clause.alias_clause = None
            columns.append(new_clause)

        method_string = f"{self.FUNCTION_NAME()}({ClauseInfo.join_clauses(columns,dialect=self._dialect)})"
        return self._concat_alias_and_column(method_string, self._alias_aggregate)
