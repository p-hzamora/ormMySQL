from __future__ import annotations
import abc
import re
import typing as tp
from ormlambda.common.interfaces.IQueryCommand import IQuery


from ormlambda.sql.types import ConditionType, ComparerTypes
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda import ConditionType as ConditionEnum
from ormlambda.sql.elements import ClauseElement

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


class Comparer(ClauseElement, IQuery):
    __visit_name__ = "comparer"

    def __init__(
        self,
        left_condition: ConditionType,
        right_condition: ConditionType,
        compare: ComparerTypes,
        flags: tp.Optional[tp.Iterable[re.RegexFlag]] = None,
        dialect: tp.Optional[Dialect] = None,
        left_alias_table: tp.Optional[str] = "{table}",
        right_alias_table: tp.Optional[str] = "{table}",
    ) -> None:
        self._compare: ComparerTypes = compare
        self._left_condition: Comparer | ClauseInfo = left_condition
        self._right_condition: Comparer | ClauseInfo = right_condition
        self._flags = flags
        self._dialect = dialect

        self.left_alias_table = left_alias_table
        self.right_alias_table = right_alias_table

    def set_dialect(self, dialect: Dialect) -> None:
        self._dialect = dialect
        return None

    def __repr__(self) -> str:
        return f"{Comparer.__name__}: {self.query}"

    def _create_clause_info(self, cond: ConditionType, dialect: Dialect, **kw) -> Comparer | ClauseInfo:
        from ormlambda import Column, ColumnProxy

        if isinstance(cond, Comparer):
            return cond

        table = None if not isinstance(cond, Column | ColumnProxy) else cond.table

        if isinstance(cond, ColumnProxy):
            kw = {
                **kw,
                "alias_table": cond.get_table_chain(),
            }

        # it a value that's not depend of any Table
        return ClauseInfo(
            table,
            cond,
            alias_clause=None,
            dialect=dialect,
            **kw,
        )

    def left_condition(self, dialect: Dialect, **kwargs) -> Comparer | ClauseInfo:
        return self._create_clause_info(self._left_condition, dialect=dialect, alias_table=self.left_alias_table, **kwargs)

    def right_condition(self, dialect: Dialect, **kwargs) -> Comparer | ClauseInfo:
        return self._create_clause_info(self._right_condition, dialect=dialect, alias_table=self.right_alias_table, **kwargs)

    @property
    def compare(self) -> ComparerTypes:
        return self._compare

    def query(self, dialect: Dialect, **kwargs) -> str:
        lcond = self.left_condition(dialect).query(dialect, **kwargs)
        rcond = self.right_condition(dialect).query(dialect, **kwargs)

        if self._flags:
            rcond = CleanValue(rcond, self._flags).clean()

        return f"{lcond} {self._compare} {rcond}"

    def __and__(self, other: Comparer, **kwargs) -> Comparer:
        # Customize the behavior of '&'
        return Comparer(self, other, "AND", **kwargs)

    def __or__(self, other: Comparer, **kwargs) -> Comparer:
        # Customize the behavior of '|'
        return Comparer(self, other, "OR", **kwargs)

    @classmethod
    def join_comparers(cls, comparers: list[Comparer], restrictive: bool = True, *, dialect) -> str:
        if not isinstance(comparers, tp.Iterable):
            raise ValueError(f"Excepted '{Comparer.__name__}' iterable not {type(comparers).__name__}")
        if len(comparers) == 1:
            comparer = comparers[0]
            return comparer.query(dialect)

        join_method = cls.__or__ if not restrictive else cls.__and__

        ini_comparer: Comparer = None
        for i in range(len(comparers) - 1):
            if ini_comparer is None:
                ini_comparer = comparers[i]
            right_comparer = comparers[i + 1]
            new_comparer = join_method(ini_comparer, right_comparer, dialect=dialect)
            ini_comparer = new_comparer
        return new_comparer.query(dialect)


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
