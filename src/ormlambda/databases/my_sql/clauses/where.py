from __future__ import annotations
import typing as tp
from ormlambda.common.abstract_classes.comparer import Comparer
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


class Where(AggregateFunctionBase):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer: Comparer, restrictive: bool = True, context: tp.Optional[ClauseInfoContext] = None) -> None:
        self._comparer: tuple[Comparer] = comparer
        self._restrictive: bool = restrictive
        self._context: tp.Optional[ClauseInfoContext] = context

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "WHERE"

    @property
    def query(self) -> str:
        if isinstance(self._comparer, tp.Iterable):
            comparer = Comparer.join_comparers(self._comparer, restrictive=self._restrictive, context=lambda: self._context)
        else:
            comparer = self._comparer
        return f"{self.FUNCTION_NAME()} {comparer}"

    @property
    def alias_clause(self) -> None:
        return None

    @staticmethod
    def join_condition(wheres: tp.Iterable[Where], restrictive: bool, context: ClauseInfoContext) -> str:
        comparers: list[Comparer] = []
        for where in wheres:
            for c in where._comparer:
                c.set_context(lambda: context)
                comparers.append(c)
        return Where(*comparers, restrictive=restrictive, context=context).query
