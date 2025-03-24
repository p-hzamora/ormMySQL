from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING

from ormlambda import ForeignKey
from ormlambda.sql.comparer import Comparer


if TYPE_CHECKING:
    from ormlambda.statements.interfaces.IStatements import IStatements_two_generic
    from ormlambda.sql.clause_info import ClauseInfo
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
    from ormlambda.common.enums.join_type import JoinType


type TupleJoinType[LTable: Table, LProp, RTable: Table, RProp] = tuple[Comparer[LTable, LProp, RTable, RProp], JoinType]


class JoinContext[TParent: Table, TRepo]:
    def __init__(self, statements: IStatements_two_generic[TParent, TRepo], joins: tuple, context: ClauseContextType) -> None:
        self._statements = statements
        self._parent: TParent = statements.model
        self._joins: Iterable[tuple[Comparer, JoinType]] = joins
        self._context: ClauseContextType = context

    def __enter__(self) -> IStatements_two_generic[TParent, TRepo]:
        for comparer, by in self._joins:
            fk_clause, alias = self.get_fk_clause(comparer)

            foreign_key: ForeignKey = ForeignKey(comparer=comparer, clause_name=alias)
            fk_clause.alias_table = foreign_key.alias
            self._context.add_clause_to_context(fk_clause)
            setattr(self._parent, alias, foreign_key)

            # TODOH []: We need to preserve the 'foreign_key' variable while inside the 'with' clause.
            # Keep in mind that 'ForeignKey.stored_calls' is cleared every time we call methods like
            # .select(), .select_one(), .insert(), .update(), or .count(). This means we only retain
            # the context from the first call of any of these methods.
            ForeignKey.stored_calls.add(foreign_key)

        return self

    def __exit__(self, type: type, error: Any, traceback: str):
        if error:
            raise error

        for comparer, _ in self._joins:
            _, attribute = self.get_fk_clause(comparer)
            fk: ForeignKey = getattr(self._parent, attribute)
            delattr(self._parent, attribute)
            del self._context._table_context[fk.tright]
        return None

    def __getattr__(self, name: str) -> TParent:
        return getattr(self._parent, name)

    def get_fk_clause(self, comparer: Comparer) -> tuple[ClauseInfo, str]:
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

        return clause_dicc[parent_table], clause_dicc[parent_table].table.__name__

