from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.elements import ClauseElement


if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
    from ormlambda.sql.types import TableType
    from ormlambda.sql.types import ColumnType
    from ormlambda.sql.types import AliasType


class Alias[T: Table](ClauseInfo[T], ClauseElement):
    __visit_name__ = "alias"

    def __init__[TProp](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: ClauseContextType = None,
        keep_asterisk: bool = False,
        preserve_context: bool = False,
        **kw,
    ):
        if not alias_clause:
            raise TypeError
        super().__init__(
            table,
            column,
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
            keep_asterisk=keep_asterisk,
            preserve_context=preserve_context,
            dtype=None,
            **kw,
        )


__all__ = ["Alias"]
