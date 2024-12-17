from __future__ import annotations
import typing as tp

from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.types import ColumnType, AliasType
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase


class Max(AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "MAX"

    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp]] | ColumnType[TProp],
        alias_clause: AliasType[ColumnType[TProp]] = 'max',
        context: tp.Optional[ClauseInfoContext] = None,
    ):

        super().__init__(
            column=column,
            alias_clause=alias_clause,
            context=context,
        )
