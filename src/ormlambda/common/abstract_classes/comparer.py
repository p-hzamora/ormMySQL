from __future__ import annotations
import typing as tp
from ormlambda.common.interfaces.IQueryCommand import IQuery


from ormlambda.types import ConditionType, ComparerTypes
from ormlambda.common.abstract_classes.clause_info import ClauseInfo

if tp.TYPE_CHECKING:
    from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
    from ormlambda import Table


class Comparer[LTable: Table, LProp, RTable: Table, RProp](IQuery):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        compare: ComparerTypes,
        context: tp.Optional[ClauseInfoContext] = None,
    ) -> None:
        self._context: tp.Optional[ClauseInfoContext] = context
        self._compare: ComparerTypes = compare
        self._left_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[LTable] = self._create_clause_info(left_condition)
        self._right_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[RTable] = self._create_clause_info(right_condition)

    def set_context(self, context: ClauseInfoContext) -> None:
        self._context = context

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.query}"

    def _create_clause_info[TTable](self, cond: ConditionType[LProp]) -> Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[TTable]:
        from ormlambda import Column

        if isinstance(cond, Comparer):
            return cond
        if isinstance(cond, Column):
            return ClauseInfo[type(cond.table)](cond.table, cond, context=self._context)
        # it a value that's not depend of any Table
        return ClauseInfo[None](None, cond, context=self._context)

    @property
    def left_condition(self) -> Comparer | ClauseInfo[LTable]:
        return self._left_condition

    @property
    def right_condition(self) -> Comparer | ClauseInfo[RTable]:
        return self._right_condition

    @property
    def compare(self) -> ComparerTypes:
        return self._compare

    @property
    def query(self) -> str:
        return f"{self._left_condition.query} {self._compare} {self._right_condition.query}"

    def __and__(self, other: Comparer) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND")

    def __or__(self, other: Comparer) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR")
