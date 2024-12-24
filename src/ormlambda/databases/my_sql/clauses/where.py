from __future__ import annotations
import typing as tp
from ormlambda.common.abstract_classes.comparer import Comparer
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase


class Where(AggregateFunctionBase):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer: Comparer, restrictive: bool = True) -> None:
        self._comparer: tuple[Comparer] = comparer
        self._restrictive: bool = restrictive

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "WHERE"

    @property
    def query(self) -> str:
        if isinstance(self._comparer, tp.Iterable):
            comparer = Comparer.join_comparers(self._comparer, restrictive=self._restrictive)
        else:
            comparer = self._comparer
        return f"{self.FUNCTION_NAME()} {comparer}"

    @property
    def alias_clause(self) -> None:
        return None

    @staticmethod
    def join_condition(wheres: tp.Iterable[Where], restrictive: bool) -> str:
        comparers = []
        for x in wheres:
            comparers.extend(x._comparer)
        return Where(*comparers, restrictive=restrictive).query
