from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
from ormlambda.sql.clause_info import AggregateFunctionBase, ClauseInfoContext
from ormlambda.sql.types import ColumnType
from ormlambda.sql.elements import ClauseElement


class GroupBy(AggregateFunctionBase, ClauseElement):
    __visit_name__ = "group_by"

    @classmethod
    def FUNCTION_NAME(self) -> str:
        return "GROUP BY"

    def __init__(self, column: ColumnType, context: ClauseInfoContext, dialect: Dialect, **kwargs):
        super().__init__(
            table=column.table,
            column=column,
            alias_table=None,
            alias_clause=None,
            context=context,
            dialect=dialect,
            **kwargs,
        )


__all__ = ["GroupBy"]
