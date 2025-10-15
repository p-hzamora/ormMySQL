from __future__ import annotations
import abc
import re
import typing as tp


from ormlambda.sql.types import ConditionType
from ormlambda.sql.types import UnionType
from ormlambda.sql.types import ComparerType
from ormlambda.sql.types import ColumnType
from ormlambda.sql.types import AliasType

from ormlambda.sql.functions.interface import IFunction
from ormlambda import ConditionType as ConditionEnum
from ormlambda.sql.elements import ClauseElement
from ormlambda.common.enums import UnionEnum

from ormlambda import ColumnProxy


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


class IComparer(IFunction):
    join: UnionEnum


type ClusterType = Comparer | ComparerCluster | ColumnType


class ComparerCluster(ClauseElement, IComparer):
    __visit_name__ = "comparer_cluster"

    def __init__(self, comp1: ClusterType, comp2: ClusterType, join: UnionType):
        self.left_comparer = comp1
        self.right_comparer = comp2
        self.join = join
        self.alias = None

    def used_columns(self) -> tp.Iterable[ColumnProxy]:
        res = []

        if isinstance(self.left_comparer, ColumnProxy):
            res.append(self.left_comparer)
        else:
            res.extend(self.left_comparer.used_columns())

        if isinstance(self.right_comparer, ColumnProxy):
            res.append(self.right_comparer)
        else:
            res.extend(self.right_comparer.used_columns())

        return res

    def __and__(self, other: ClusterType) -> ComparerCluster:
        # Customize the behavior of '&'
        return ComparerCluster(self, other, UnionEnum.AND)

    def __or__(self, other: ClusterType) -> ComparerCluster:
        # Customize the behavior of '|'
        return ComparerCluster(self, other, UnionEnum.OR)

    def __repr__(self):
        return f"{ComparerCluster.__name__}: {self.left_comparer.__repr__()} {self.right_comparer.__repr__()}"


class Comparer(ClauseElement, IComparer):
    __visit_name__ = "comparer"

    def __init__(
        self,
        left_condition: ConditionType,
        right_condition: ConditionType,
        compare: ComparerType,
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
        alias: tp.Optional[AliasType] = None,
    ) -> None:
        self._compare: ComparerType = compare
        self.left_condition: ConditionType = left_condition
        self.right_condition: ConditionType = right_condition
        self._flags = flags
        self.join: UnionType = UnionEnum.AND
        self.alias: tp.Optional[str] = alias

    @property
    def dtype(self) -> tp.Any: ...

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.left_condition} {self._compare} {self.right_condition}"

    @property
    def compare(self) -> ComparerType:
        return self._compare

    def __and__(self, other: Comparer) -> ComparerCluster:
        # Customize the behavior of '&'
        return ComparerCluster(self, other, UnionEnum.AND)

    def __or__(self, other: Comparer) -> ComparerCluster:
        # Customize the behavior of '|'
        return ComparerCluster(self, other, UnionEnum.OR)

    def __add__(self, other: ColumnType):
        """a + b"""
        return ComparerCluster(self, other, "+")

    def __sub__(self, other: ColumnType):
        """a - b"""
        return ComparerCluster(self, other, "-")

    def __mul__(self, other: ColumnType):
        """a * b"""
        return ComparerCluster(self, other, "*")

    def __truediv__(self, other: ColumnType):
        """a / b"""
        return ComparerCluster(self, other, "/")

    def __floordiv__(self, other: ColumnType):
        """a // b"""
        return ComparerCluster(self, other, "//")

    def __mod__(self, other: ColumnType):
        """a % b"""
        return ComparerCluster(self, other, "%")

    def __pow__(self, other: ColumnType):
        """a ** b"""
        return ComparerCluster(self, other, "**")

    def used_columns(self) -> tp.Iterable[ColumnProxy]:
        res = []

        if isinstance(self.left_condition, ColumnProxy):
            res.append(self.left_condition)

        if isinstance(self.right_condition, ColumnProxy):
            res.append(self.right_condition)

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
