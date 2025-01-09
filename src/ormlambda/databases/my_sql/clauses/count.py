from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase, ClauseInfo
from ormlambda.common.abstract_classes.clause_info_context import ClauseContextType, ClauseInfoContext


import typing as tp
from ormlambda.types import ColumnType, AliasType
from ormlambda import Column
from ormlambda.utils.foreign_key import ForeignKey
from ormlambda.utils.table_constructor import Table


class Count[*Ts](AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "COUNT"

    def __init__[TProp](
        self,
        values: ColumnType[Ts] | tuple[ColumnType[Ts], ...],
        alias_clause: AliasType[ColumnType[TProp]] = "count",
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            column=values,
            alias_clause=alias_clause,
            context=context,
        )

        if not isinstance(values, tp.Iterable):
            values = (values,)

        columns: list[ClauseInfo] = []
        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None
        for clause in self._convert_into_clauseInfo(self.unresolved_column, context):
            new_clause = clause
            new_clause.alias_clause = None
            columns.append(new_clause)

    @tp.override
    @property
    def query(self) -> str:
        columns: list[str] = []

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None

        for clause in self._convert_into_clauseInfo(self.unresolved_column, context):
            new_clause = clause
            new_clause.alias_clause = None
            columns.append(new_clause)
        return self._concat_alias_and_column(f"{self.FUNCTION_NAME()}({ClauseInfo.join_clauses(columns)})", self._alias_clause)

    @tp.override
    @staticmethod
    def _convert_into_clauseInfo[TProp](columns: ClauseInfo | ColumnType[TProp], context: ClauseContextType) -> list[ClauseInfo]:
        type ClusterType = ColumnType | str | ForeignKey
        dicc_type: dict[ClusterType, tp.Callable[[ClusterType], ClauseInfo]] = {
            Column: lambda column: ClauseInfo(column.table, column, context=context),
            ClauseInfo: lambda column: column,
            ForeignKey: lambda column: ClauseInfo(table=None, column="*"),
            Table: lambda column: ClauseInfo(table=None, column="*"),
            "default": lambda column: ClauseInfo(table=None, column=column, context=context),
        }

        all_clauses: list[ClauseInfo] = []
        if isinstance(columns, str) or not isinstance(columns, tp.Iterable):
            columns = (columns,)
        for value in columns:
            all_clauses.append(dicc_type.get(type(value), dicc_type["default"])(value))

        return all_clauses
