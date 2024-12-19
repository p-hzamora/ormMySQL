from __future__ import annotations
import typing as tp
from ormlambda.common.abstract_classes.comparer import Comparer
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, AggregateFunctionBase


class Where(AggregateFunctionBase):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer: Comparer) -> None:
        self._comparer: tuple[Comparer] = comparer

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "WHERE"

    # FIXME [ ]: that's an error. We need to keep in mind that left_condition could be Compare
    @property
    def left_condition(self) -> ClauseInfo:
        return self._comparer.left_condition

    @property
    def right_condition(self) -> ClauseInfo:
        return self._comparer.right_condition

    @property
    def query(self) -> str:
        if isinstance(self._comparer, tp.Iterable):
            comparer = Comparer.join_comparers(self._comparer)
        else:
            comparer = self._comparer
        return f"{self.FUNCTION_NAME()} {comparer}"

    @property
    def alias_clause(self) -> None:
        return None
