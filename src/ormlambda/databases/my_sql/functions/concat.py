from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


import typing as tp
from ormlambda.types import ColumnType, AliasType


class Concat[*Ts](AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "CONCAT"

    def __init__[TProp](
        self,
        values: ColumnType[Ts] | tuple[ColumnType[Ts], ...],
        alias_clause: AliasType[ColumnType[TProp]] = "concat",
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        super().__init__(
            column=values,
            alias_clause=alias_clause,
            context=context,
        )
