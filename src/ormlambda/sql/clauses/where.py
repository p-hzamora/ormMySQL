from __future__ import annotations
import typing as tp
from ormlambda import ColumnProxy
from ormlambda.sql.comparer import Comparer
from ormlambda.sql.elements import ClauseElement

if tp.TYPE_CHECKING:
    from ormlambda.statements.types import WhereTypes


class Where[T](ClauseElement):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    __visit_name__ = "where"

    def __init__(
        self,
        *comparer: WhereTypes,
        restrictive: bool = True,
    ) -> None:
        self.comparer: set[Comparer] = set(comparer)
        self.restrictive: bool = restrictive

    def used_columns(self) -> tp.Iterable[ColumnProxy]:
        res = []

        for comparer in self.comparer:
            if isinstance(comparer.left_condition, ColumnProxy):
                res.append(comparer.left_condition)

            if isinstance(comparer.right_condition, ColumnProxy):
                res.append(comparer.right_condition)

        return res

    def add_comparers(self, comparers: tp.Iterable[Comparer]) -> None:
        if not isinstance(comparers, tp.Iterable):
            comparers = [comparers]

        for comparer in comparers:
            self.comparer.add(comparer)


__all__ = ["Where"]
