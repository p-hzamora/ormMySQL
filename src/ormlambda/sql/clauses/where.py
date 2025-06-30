from __future__ import annotations
import typing as tp
from ormlambda.sql.comparer import Comparer
from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.elements import ClauseElement

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Where(AggregateFunctionBase, ClauseElement):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    __visit_name__ = "where"

    def __init__(
        self,
        *comparer: Comparer,
        restrictive: bool = True,
    ) -> None:
        self._comparer: tuple[Comparer] = comparer
        self._restrictive: bool = restrictive

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "WHERE"

    def compile(self, dialect: Dialect, **kwargs) -> str:
        if isinstance(self._comparer, tp.Iterable):
            comparer = Comparer.join_comparers(
                self._comparer,
                restrictive=self._restrictive,
                dialect=dialect,
                **kwargs,
            )
        else:
            comparer = self._comparer
        return f"{self.FUNCTION_NAME()} {comparer}"

    @property
    def alias_clause(self) -> None:
        return None

    @classmethod
    def join_condition(cls, wheres: tp.Iterable[Where], restrictive: bool, dialect: Dialect = None) -> str:
        if not isinstance(wheres, tp.Iterable):
            wheres = (wheres,)

        comparers: list[Comparer] = []
        for where in wheres:
            for c in where._comparer:
                comparers.append(c)
        return cls(*comparers, restrictive=restrictive).query(dialect=dialect)


__all__ = ["Where"]
