from __future__ import annotations
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.types import ColumnType
from ormlambda.sql.elements import ClauseElement


class GroupBy(AggregateFunctionBase, ClauseElement):
    __visit_name__ = "group_by"

    @classmethod
    def FUNCTION_NAME(self) -> str:
        return "GROUP BY"

    def __init__(self, column: ColumnType, dialect: Dialect, **kwargs):
        if isinstance(column, Iterable):
            column = column[0]
        super().__init__(
            table=column.table,
            column=column,
            alias_table=None,
            alias_clause=None,
            dialect=dialect,
            **kwargs,
        )


__all__ = ["GroupBy"]
