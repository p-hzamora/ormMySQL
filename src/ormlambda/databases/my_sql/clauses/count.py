from __future__ import annotations
from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType

from ormlambda.sql.types import AliasType, ColumnType

from ormlambda import Table

import typing as tp

from ormlambda.sql.types import ASTERISK

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.types import ColumnType, AliasType, TableType


class Count[T: Table](AggregateFunctionBase[T]):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "COUNT"

    def __init__[TProp: Table](
        self,
        element: ColumnType[T] | TableType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = "count",
        context: ClauseContextType = None,
        keep_asterisk: bool = True,
        preserve_context: bool = True,
    ) -> None:
        table = self.extract_table(element)
        column = element if self.is_column(element) else ASTERISK

        super().__init__(
            table=table if (alias_table or (context and table in context._table_context)) else None,
            column=column,
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=keep_asterisk,
            preserve_context=preserve_context,
        )
