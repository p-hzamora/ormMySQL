from __future__ import annotations
import abc
import re
import typing as tp


from ormlambda.sql.types import ConditionType, ComparerTypes
from ormlambda.sql.clause_info import ClauseInfo, IAggregate
from ormlambda import ConditionType as ConditionEnum
from ormlambda.sql.elements import ClauseElement

from ormlambda import ColumnProxy

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


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


class Comparer(ClauseElement, IAggregate):
    __visit_name__ = "comparer"

    def __init__(
        self,
        left_condition: ConditionType,
        right_condition: ConditionType,
        compare: ComparerTypes,
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
    ) -> None:
        self._compare: ComparerTypes = compare
        self._left_condition: ConditionType = left_condition
        self._right_condition: ConditionType = right_condition
        self._flags = flags

    @property
    def dtype(self) -> tp.Any: ...

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self._left_condition} {self._compare} {self._right_condition}"

    def left_condition(self, dialect: Dialect, **kwargs) -> Comparer | ClauseInfo:
        if isinstance(self._left_condition, ColumnProxy | Comparer):
            return self._left_condition.compile(dialect=dialect, **kwargs).string

        if isinstance(self._left_condition, str):
            # TODOL []: Check if we can use the Caster class to wrap the condition instead of hardcoding it.
            return f"'{self._left_condition}'"
        return self._left_condition

    def right_condition(self, dialect: Dialect, **kwargs) -> Comparer | ClauseInfo:
        if isinstance(self._right_condition, ColumnProxy | Comparer):
            return self._right_condition.compile(dialect=dialect, **kwargs).string

        if isinstance(self._right_condition, str):
            # TODOL []: Check if we can use the Caster class to wrap the condition instead of hardcoding it.
            return f"'{self._right_condition}'"
        return self._right_condition

    @property
    def compare(self) -> ComparerTypes:
        return self._compare

    def __and__(self, other: Comparer, **kwargs) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND", **kwargs)

    def __or__(self, other: Comparer, **kwargs) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR", **kwargs)

    @classmethod
    def join_comparers(cls, comparers: list[Comparer], restrictive: bool = True, *, dialect, **kwargs) -> str:
        if not isinstance(comparers, tp.Iterable):
            raise ValueError(f"Excepted '{Comparer.__name__}' iterable not {type(comparers).__name__}")

        if len(comparers) == 1:
            comparer = comparers[0]
            return comparer.compile(dialect, alias_clause=None, **kwargs).string

        join_method = cls.__or__ if not restrictive else cls.__and__

        ini_comparer: Comparer = None
        for i in range(len(comparers) - 1):
            if ini_comparer is None:
                ini_comparer = comparers[i]
            right_comparer = comparers[i + 1]
            new_comparer = join_method(ini_comparer, right_comparer)
            ini_comparer = new_comparer

        res = new_comparer.compile(dialect, alias_clause=None, **kwargs)
        return res.string

    def used_columns(self) -> tp.Iterable[ColumnProxy]:
        res = []

        if isinstance(self._left_condition, ColumnProxy):
            res.append(self._left_condition)

        if isinstance(self._right_condition, ColumnProxy):
            res.append(self._right_condition)

        return res


class Regex(Comparer):
    def __init__(
        self,
        left_condition: ConditionType,
        right_condition: ConditionType,
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
    ):
        super().__init__(
            left_condition=left_condition,
            right_condition=right_condition,
            compare=ConditionEnum.REGEXP.value,
            flags=flags,  # Pass as a named parameter instead
        )


class Like(Comparer):
    def __init__(
        self,
        left_condition: ConditionType,
        right_condition: ConditionType,
    ):
        super().__init__(left_condition, right_condition, ConditionEnum.LIKE.value)
