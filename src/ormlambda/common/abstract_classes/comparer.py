from __future__ import annotations
import typing as tp
from ormlambda.common.interfaces.IQueryCommand import IQuery


from ormlambda.types import ComparerType, ColumnType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo

type ConditionType[L, *R] = Comparer[L, *R] | ColumnType
type UnionType = tp.Literal["AND", "OR", ""]
type ComparerTypes = ComparerType | UnionType


class Comparer[LProp, *RProp](IQuery):
    def __init__(self, left_condition: ConditionType[LProp], right_condition: ConditionType[RProp], compare: ComparerTypes) -> None:
        self._left_condition: Comparer | ClauseInfo = self._create_clause_info(left_condition)
        self._right_condition: Comparer | ClauseInfo = self._create_clause_info(right_condition)
        self._compare: ComparerTypes = compare

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.query}"

    def _create_clause_info(self, cond: ConditionType[LProp]) -> Comparer | ClauseInfo:
        from ormlambda import Column

        if isinstance(cond, Comparer):
            return cond
        if isinstance(cond, Column):
            return ClauseInfo(cond.table, cond)
        # it a value that's not depend of any Table
        return ClauseInfo(None, cond)

    @property
    def query(self) -> str:
        return f"{self._left_condition.query} {self._compare} {self._right_condition.query}"

    def __and__(self, other: Comparer) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND")

    def __or__(self, other: Comparer) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR")
