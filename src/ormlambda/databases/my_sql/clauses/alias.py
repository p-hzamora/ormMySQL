import typing as tp

from ormlambda.types import AliasType, ColumnType
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase, ClauseInfo
from ormlambda.utils.foreign_key import ForeignKey
from ormlambda.utils.column import Column
from ormlambda.utils.table_constructor import Table
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


class Alias(ClauseInfo[None]):
    def __init__[TProp](
        self,
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[None]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[None]]] = None,
        context: ClauseInfoContext = None,
        table: Table = None,
    ):
        if isinstance(column, AggregateFunctionBase):
            ci = column
            ci._table = self._extract_table(ci.unresolved_column)
        else:
            ci = AggregateFunctionBase._convert_into_clauseInfo(column, context)[0]
        ci.alias_clause = alias_clause
        ci.alias_table = alias_table if alias_table else ci.alias_table
        super().__init__(
            table=ci.table,
            column=ci._column,
            alias_table=ci.alias_table,
            alias_clause=ci.alias_clause,
            context=ci.context,
        )

    @tp.override
    @property
    def query(self) -> str:
        return super().query

    def _extract_table[TProp](self, obj: ColumnType[TProp]) -> tp.Optional[Table]:
        if isinstance(obj, type) and issubclass(obj, Table):  # noqa: F821
            return obj

        if isinstance(obj, ForeignKey):
            return obj.tright
        if isinstance(obj, Column):
            return obj.table
        return None
