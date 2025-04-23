import typing as tp
from ormlambda import Table
from ormlambda.sql.clause_info import AggregateFunctionBase, ClauseInfoContext
from ormlambda.sql.types import ColumnType


class _GroupBy[T: tp.Type[Table], *Ts, TProp](AggregateFunctionBase):
    @classmethod
    def FUNCTION_NAME(self) -> str:
        return "GROUP BY"

    def __init__(
        self,
        column: ColumnType,
        context: ClauseInfoContext,
        **kwargs,
    ):
        super().__init__(
            table=column.table,
            column=column,
            alias_table=None,
            alias_clause=None,
            context=context,
            **kwargs,
        )

    @property
    def query(self) -> str:
        column = self._create_query()
        return f"{self.FUNCTION_NAME()} {column}"

__all__ = ["_GroupBy"]
