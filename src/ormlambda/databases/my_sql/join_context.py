from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING, Optional

from ormlambda import ForeignKey
from ormlambda.common.abstract_classes.comparer import Comparer


if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.clause_info import ClauseInfo
    from ormlambda import Table
    from ormlambda.common.interfaces import IStatements_two_generic
    from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
    from ormlambda.common.enums.join_type import JoinType


type TupleJoinType[LTable: Table, LProp, RTable: Table, RProp] = tuple[str, Comparer[LTable, LProp, RTable, RProp], JoinType]


class JoinContext[TParent: Table, *T, TRepo]:
    def __init__(self, statements: IStatements_two_generic[TParent, *T, TRepo], joins: tuple[*T], context: Optional[ClauseInfoContext]) -> None:
        self._statements = statements
        self._parent: TParent = statements.model
        self._joins: Iterable[tuple[str, Comparer, JoinType]] = joins
        self._context: Optional[ClauseInfoContext] = context

    def __enter__(self) -> IStatements_two_generic[TParent, *T, TRepo]:
        for alias, comparer, by in self._joins:
            foreign_key = ForeignKey(comparer=comparer, clause_name=alias)
            self._context.add_clause_to_context(self.get_fk_table(comparer))
            setattr(self, alias, foreign_key)
        return self

    def __exit__(self, type: type, value: Any, traceback: str):
        if value:
            raise value

        for alias, _, _ in self._joins:
            delattr(self._parent, alias)
        return None

    def __getattr__(self, name: str) -> TParent:
        return getattr(self._statements, name)

    def get_fk_table(self, comparer: Comparer) -> ClauseInfo:
        clause_dicc: dict[Table, ClauseInfo] = {
            comparer.left_condition.table: comparer.left_condition,
            comparer.right_condition.table: comparer.right_condition,
        }
        conditions = set([comparer.left_condition.table, comparer.right_condition.table])
        model = set([self._statements.model])

        parent_table = conditions.difference(model).pop()

        return clause_dicc[parent_table]


# type JoinCondition = tuple[str,Comparer[],JoinType]
