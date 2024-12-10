from typing import Any, Iterable, TYPE_CHECKING

from ormlambda import Table, ForeignKey
from ormlambda.common.abstract_classes.comparer import Comparer

if TYPE_CHECKING:
    from ormlambda.common.enums.join_type import JoinType

type TupleJoinType[T] = tuple[str, T, Comparer]


class JoinContext[TParent, *T]:
    def __init__(self, parent: TParent, joins: tuple[*T]) -> None:
        self._parent: TParent = parent
        self._joins: Iterable[tuple[str, *T, Comparer]] = joins

    def __enter__(self) -> Iterable[tuple[*T, str, Comparer]]:
        for join in self._joins:
            for name,comparer in join:
                foreign_key = ForeignKey(comparer=comparer, clause_name=name)
                setattr(self._parent, name, foreign_key)
        return self._parent

    def __exit__(self, type: type, value: Any, traceback: str):
        for name, _ in self._joins:
            delattr(self._parent, name)
        return None


# type JoinCondition = tuple[str,Comparer[],JoinType]