from __future__ import annotations
import abc
import re
import typing as tp
from ormlambda.common.interfaces.IQueryCommand import IQuery


from ormlambda.sql.types import ConditionType, ComparerTypes
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda import ConditionType as ConditionEnum

if tp.TYPE_CHECKING:
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
    from ormlambda.sql import Table


class ICleaner(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def clean(value: str): ...


class IgnoreCase(ICleaner):
    @staticmethod
    def clean(value: str) -> str:
        return value.lower()


DICC_FLAGS = {
    re.IGNORECASE: IgnoreCase,
}


class CleanValue:
    def __init__(self, name: str, *flags: re.RegexFlag):
        self._flags = flags
        self._filename: str = name

    def clean(self) -> str:
        temp_name = self._filename
        for flag in self._flags:
            cleaner = DICC_FLAGS.get(flag, None)
            if cleaner:
                temp_name = cleaner.clean(temp_name)
        return temp_name


class Comparer[LTable: Table, LProp, RTable: Table, RProp](IQuery):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        compare: ComparerTypes,
        context: ClauseContextType = None,
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
    ) -> None:
        self._context: ClauseContextType = context
        self._compare: ComparerTypes = compare
        self._left_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[LTable] = left_condition
        self._right_condition: Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[RTable] = right_condition
        self._flags = flags

    def set_context(self, context: ClauseContextType) -> None:
        self._context = context

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.query}"

    def _create_clause_info[TTable](self, cond: ConditionType[LProp]) -> Comparer[LTable, LProp, RTable, RProp] | ClauseInfo[TTable]:
        from ormlambda import Column

        if isinstance(cond, Comparer):
            return cond
        if isinstance(cond, Column):
            return ClauseInfo(cond.table, cond, alias_clause=None, context=self._context)
        # it a value that's not depend of any Table
        return ClauseInfo(None, cond, alias_clause=None, context=self._context)

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
        lcond = self.left_condition.query
        rcond = self.right_condition.query

        if self._flags:
            rcond = CleanValue(rcond, self._flags).clean()

        return f"{lcond} {self._compare} {rcond}"

    def __and__(self, other: Comparer, context: ClauseContextType = None) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND", context=context)

    def __or__(self, other: Comparer, context: ClauseContextType = None) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR", context=context)

    @classmethod
    def join_comparers(cls, comparers: list[Comparer], restrictive: bool = True, context: ClauseContextType = None) -> str:
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
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
    ):
        super().__init__(
            left_condition=left_condition,
            right_condition=right_condition,
            compare=ConditionEnum.REGEXP.value,
            context=context,
            flags=flags,  # Pass as a named parameter instead
        )


class Like[LProp, RProp](Comparer[None, LProp, None, RProp]):
    def __init__(
        self,
        left_condition: ConditionType[LProp],
        right_condition: ConditionType[RProp],
        context: ClauseContextType = None,
    ):
        super().__init__(left_condition, right_condition, ConditionEnum.LIKE.value, context)
