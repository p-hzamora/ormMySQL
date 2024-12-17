from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase, ClauseInfo
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


import typing as tp
from ormlambda.types import ColumnType, AliasType
from ormlambda import Column


class Count[*Ts](AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "COUNT"

    def __init__[TProp](
        self,
        values: ColumnType[Ts] | tuple[ColumnType[Ts], ...],
        alias_clause: AliasType[ColumnType[TProp]] = "count",
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        all_clauses: list[ClauseInfo] = []

        if not isinstance(values, tp.Iterable):
            values = (values,)
        for value in values:
            if isinstance(value, Column):
                all_clauses.append(ClauseInfo(value.table, value, context=context))
            else:
                all_clauses.append(ClauseInfo(table=None, column=value, context=context))

        super().__init__(
            column=all_clauses,
            alias_clause=alias_clause,
            context=context,
        )
