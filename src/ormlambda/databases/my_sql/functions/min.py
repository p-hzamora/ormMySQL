from __future__ import annotations
import typing as tp

from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda.types import ColumnType, AliasType
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase


class Min(AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "MIN"

    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp], ...] | ColumnType[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = "min",
        context: tp.Optional[ClauseInfoContext] = None,
    ):
        super().__init__(
            column=column,
            alias_clause=alias_clause,
            context=context,
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
        return self._concat_alias_and_column(method_string, self._alias_clause)
