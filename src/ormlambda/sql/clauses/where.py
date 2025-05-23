from __future__ import annotations
import typing as tp
from ormlambda.sql.comparer import Comparer
from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType


class _Where(AggregateFunctionBase):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer: Comparer, restrictive: bool = True, context: ClauseContextType = None) -> None:
        self._comparer: tuple[Comparer] = comparer
        self._restrictive: bool = restrictive
        self._context: ClauseContextType = context if context else ClauseInfoContext()

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "WHERE"

    @property
    def query(self) -> str:
        if isinstance(self._comparer, tp.Iterable):
            context = ClauseInfoContext(table_context=self._context._table_context)
            comparer = Comparer.join_comparers(self._comparer, restrictive=self._restrictive, context=context)
        else:
            comparer = self._comparer
        return f"{self.FUNCTION_NAME()} {comparer}"

    @property
    def alias_clause(self) -> None:
        return None

    @classmethod
    def join_condition(cls, wheres: tp.Iterable[_Where], restrictive: bool, context: ClauseInfoContext) -> str:
        if not isinstance(wheres, tp.Iterable):
            wheres = (wheres,)

        comparers: list[Comparer] = []
        for where in wheres:
            for c in where._comparer:
                c.set_context(context)
                comparers.append(c)
        return cls(*comparers, restrictive=restrictive, context=context).query


__all__ = ["_Where"]
