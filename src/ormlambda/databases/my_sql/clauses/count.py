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
        table: ColumnType[T] | TableType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = "count",
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            table=self.extract_table(table) if alias_table else None,
            column="*",
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=True,
            preserve_context=True,
        )
