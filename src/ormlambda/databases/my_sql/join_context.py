from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING

from ormlambda import ForeignKey
from ormlambda.common.abstract_classes.comparer import Comparer


if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.clause_info import ClauseInfo
    from ormlambda import Table
    from ormlambda.common.interfaces import IStatements_two_generic
    from ormlambda.common.abstract_classes.clause_info_context import ClauseContextType
    from ormlambda.common.enums.join_type import JoinType


type TupleJoinType[LTable: Table, LProp, RTable: Table, RProp] = tuple[str, Comparer[LTable, LProp, RTable, RProp], JoinType]


class JoinContext[TParent: Table, *T, TRepo]:
    def __init__(self, statements: IStatements_two_generic[TParent, *T, TRepo], joins: tuple[*T], context: ClauseContextType) -> None:
        self._statements = statements
        self._parent: TParent = statements.model
        self._joins: Iterable[tuple[str, Comparer, JoinType]] = joins
        self._context: ClauseContextType = context

    def __enter__(self) -> IStatements_two_generic[TParent, *T, TRepo]:
        for alias, comparer, by in self._joins:
            foreign_key: ForeignKey = ForeignKey(comparer=comparer, clause_name=alias)
            fk_clause = self.get_origin_table_in_fk(comparer)
            fk_clause.alias_table = foreign_key.alias
            self._context.add_clause_to_context(fk_clause)
            setattr(self._parent, alias, foreign_key)
        return self

    def __exit__(self, type: type, error: Any, traceback: str):
        if error:
            raise error

        for attribute, _, _ in self._joins:
            fk: ForeignKey = getattr(self._parent, attribute)
            delattr(self._parent, attribute)
            del self._context._table_context[fk.tright]
            del self._context._alias_context[fk.alias]
        return None

    def __getattr__(self, name: str) -> TParent:
        return getattr(self._parent, name)

    def get_origin_table_in_fk(self, comparer: Comparer) -> ClauseInfo:
        """
        In this method the 'comparer' attributes always should be a one by one comparison.
        Not a combining of Comparers like when using () & () | () ... operator

        >>> A.fk_b == B.pk_b # Correct
        >>> (A.fk_b == B.pk_b) & (B.fk_c == C.pk_c) # Incorrect
        """
        clause_dicc: dict[Table, ClauseInfo] = {
            comparer.left_condition.table: comparer.left_condition,
            comparer.right_condition.table: comparer.right_condition,
        }
        conditions = set([comparer.left_condition.table, comparer.right_condition.table])
        model = set([self._statements.model])

        parent_table = conditions.difference(model).pop()

        return clause_dicc[parent_table]


# type JoinCondition = tuple[str,Comparer[],JoinType]
