from __future__ import annotations
import typing as tp
from ormlambda.common.interfaces.IQueryCommand import IQuery


from ormlambda.types import ConditionType, ComparerTypes
from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda import ConditionType as ConditionEnum

if tp.TYPE_CHECKING:
    from ormlambda.common.abstract_classes.clause_info_context import ClauseContextType
    from ormlambda import Table

type CallableContextType = tp.Callable[[], ClauseContextType]


class Comparer[LTable: Table, LProp, RTable: Table, RProp](IQuery):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        compare: ComparerTypes,
        context: CallableContextType = lambda: None,
    ) -> None:
        self._context: CallableContextType = context
        self._compare: ComparerTypes = compare
        self._left_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[LTable] = left_condition
        self._right_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[RTable] = right_condition

    def set_context(self, context: CallableContextType) -> None:
        self._context = context

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.query}"

    def _create_clause_info[TTable](self, cond: ConditionType[LProp]) -> Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[TTable]:
        from ormlambda import Column

        if isinstance(cond, Comparer):
            return cond
        if isinstance(cond, Column):
            return ClauseInfo[type(cond.table)](cond.table, cond, alias_clause=None, context=self._context())
        # it a value that's not depend of any Table
        return ClauseInfo[None](None, cond, alias_clause=None, context=self._context())

    @property
    def left_condition(self) -> Comparer | ClauseInfo[LTable]:
        return self._create_clause_info(self._left_condition)

    @property
    def right_condition(self) -> Comparer | ClauseInfo[RTable]:
        return self._create_clause_info(self._right_condition)

    @property
    def compare(self) -> ComparerTypes:
        return self._compare

    @property
    def query(self) -> str:
        return f"{self.left_condition.query} {self._compare} {self.right_condition.query}"

    def __and__(self, other: Comparer, context: CallableContextType = lambda: None) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND", context=context)

    def __or__(self, other: Comparer, context: CallableContextType = lambda: None) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR", context=context)

    @classmethod
    def join_comparers(cls, comparers: list[Comparer], restrictive: bool = True, context: CallableContextType = lambda: None) -> str:
        if not isinstance(comparers, tp.Iterable):
            raise ValueError(f"Excepted '{Comparer.__name__}' iterable not {type(comparers).__name__}")
        if len(comparers) == 1:
            comparer = comparers[0]
            comparer.set_context(context)
            return comparer.query

        join_method = cls.__or__ if not restrictive else cls.__and__

        ini_comparer: Comparer = None
        for i in range(len(comparers) - 1):
            if ini_comparer is None:
                ini_comparer = comparers[i]
                ini_comparer.set_context(context)
            right_comparer = comparers[i + 1]
            right_comparer.set_context(context)
            new_comparer = join_method(ini_comparer, right_comparer, context=context)
            ini_comparer = new_comparer
        return new_comparer.query


class Regex[LProp, RProp](Comparer[None, LProp, None, RProp]):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        context: ClauseContextType = None,
    ):
        super().__init__(left_condition, right_condition, ConditionEnum.REGEXP.value, context)


class Like[LProp, RProp](Comparer[None, LProp, None, RProp]):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        context: ClauseContextType = None,
    ):
        super().__init__(left_condition, right_condition, ConditionEnum.LIKE.value, context)
