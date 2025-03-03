from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.clause_info import AggregateFunctionBase


class Min(AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "MIN"

    def __init__[TProp](
        self,
        elements: tuple[ColumnType[TProp], ...] | ColumnType[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = "min",
        context: ClauseContextType = None,
    ):
        super().__init__(
            table=None,
            column=elements,
            alias_table=None,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=False,
            preserve_context=False,
        )

    @tp.override
    @property
    def query(self) -> str:
        columns: list[str] = []

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None
        for clause in self._convert_into_clauseInfo(self.unresolved_column, context):
            new_clause = clause
            new_clause.alias_clause = None
            columns.append(new_clause)

        method_string = f"{self.FUNCTION_NAME()}({ClauseInfo.join_clauses(columns)})"
        return self._concat_alias_and_column(method_string, self._alias_aggregate)
