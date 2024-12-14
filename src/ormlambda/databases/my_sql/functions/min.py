from __future__ import annotations
import typing as tp

from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.types import ColumnType, AliasType
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase, ClauseInfo

if tp.TYPE_CHECKING:
    from ormlambda import Table

class Min(AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "MIN"

    def __init__[T:Table,TProp](
        self,
        column: tuple[ColumnType[TProp]] | ColumnType[TProp],
        alias_table: AliasType[ColumnType[TProp]] = None,
        alias_clause: AliasType[ColumnType[TProp]] = 'min',
        context: tp.Optional[ClauseInfoContext] = None,
    ):
        if isinstance(column,tp.Iterable):
            column = ClauseInfo.join_clauses([ClauseInfo[T](x.table,x,alias_table=alias_table,context=context) for x in column])
        else:
            column = ClauseInfo[T](column.table,column,alias_table=alias_table,context=context)
            
        super().__init__(
            column=column,
            alias_clause=alias_clause,
            context=context,
        )
