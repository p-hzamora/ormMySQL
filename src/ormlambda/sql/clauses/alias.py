from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info import ClauseInfo

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
    from ormlambda.sql.types import TableType
    from ormlambda.sql.types import ColumnType
    from ormlambda.sql.types import AliasType


class _Alias[T: Table](ClauseInfo[T]):
    def __init__[TProp](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: ClauseContextType = None,
        keep_asterisk: bool = False,
        preserve_context: bool = False,
    ):
        if not alias_clause:
            raise TypeError
        super().__init__(table, column, alias_table, alias_clause, context, keep_asterisk, preserve_context)


__all__ = ["_Alias"]
