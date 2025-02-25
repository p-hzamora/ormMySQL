from __future__ import annotations
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseContextType

from ormlambda.types import AliasType, ColumnType

from ormlambda.utils.table_constructor import Table

import typing as tp

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.types import ColumnType, AliasType, TableType


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

        super().__init__(
            table=table if (alias_table or (context and table in context._table_context)) else None,
            column="*",
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=keep_asterisk,
            preserve_context=preserve_context,
        )
