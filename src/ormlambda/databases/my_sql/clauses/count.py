from __future__ import annotations
from ormlambda.sql.clauses import Count
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType

from ormlambda.sql.types import AliasType, ColumnType

from ormlambda import Table

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.types import ColumnType, AliasType, TableType


class Count[T: Table](Count[T]):
    def __init__[TProp: Table](
        self,
        element: ColumnType[T] | TableType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = "count",
        context: ClauseContextType = None,
        keep_asterisk: bool = True,
        preserve_context: bool = True,
    ) -> None:
        super().__init__(
            element=element,
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=keep_asterisk,
            preserve_context=preserve_context,
        )
