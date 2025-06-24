from __future__ import annotations

from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.types import ColumnType, AliasType


type ConcatResponse[TProp] = tuple[str | ColumnType[TProp]]




class Concat[T](AggregateFunctionBase[T]):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "CONCAT"
        # TODOL []: remove this method wherever possible

    def __init__[TProp](
        self,
        values: ConcatResponse[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = "concat",
    ) -> None:
        super().__init__(
            table=None,
            column=values,
            alias_clause=alias_clause,
            dtype=str,
        )

