from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING

from ormlambda import ForeignKey
from ormlambda.sql.comparer import Comparer


if TYPE_CHECKING:
    from ormlambda.statements.interfaces.IStatements import IStatements
    from ormlambda.sql.clause_info import ClauseInfo
    from ormlambda import Table
    from ormlambda.common.enums.join_type import JoinType
    from ormlambda.dialects import Dialect


type TupleJoinType[LTable: Table, LProp, RTable: Table, RProp] = tuple[Comparer]


class JoinContext[TParent: Table]:
    def __init__(
        self,
        statements: IStatements[TParent],
        joins: tuple,
        dialect: Dialect,
    ) -> None:
        self._statements = statements
        self._parent: TParent = statements.model
        self._joins: Iterable[tuple[Comparer, JoinType]] = joins
        self._dialect: Dialect = dialect

    def __enter__(self) -> IStatements[TParent]:
        for comparer, by in self._joins:
            fk_clause, alias = self.get_fk_clause(comparer)

            foreign_key: ForeignKey = ForeignKey(comparer=comparer, clause_name=alias, keep_alive=True, dialect=self._dialect)
            fk_clause.alias_table = foreign_key.get_alias(self._dialect)
            setattr(self._parent, alias, foreign_key)

            # TODOH [x]: We need to preserve the 'foreign_key' variable while inside the 'with' clause.
            # Keep in mind that 'ForeignKey.stored_calls' is cleared every time we call methods like
            # .select(), .select_one(), .insert(), .update(), or .count(). This means we only retain
            # the context from the first call of any of these methods.
            # FIXME [ ]: See how to deal with context when using JoinContext class and PATH_CONTEXT

        return self

    def __exit__(self, type: type, error: Any, traceback: str):
        if error:
            raise error

        for comparer, _ in self._joins:
            _, attribute = self.get_fk_clause(comparer)
            delattr(self._parent, attribute)
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
            comparer.left_condition(self._dialect).table: comparer.left_condition(self._dialect),
            comparer.right_condition(self._dialect).table: comparer.right_condition(self._dialect),
        }
        conditions = set([comparer.left_condition(self._dialect).table, comparer.right_condition(self._dialect).table])
        model = set([self._statements.model])

        parent_table = conditions.difference(model).pop()

        return clause_dicc[parent_table], clause_dicc[parent_table].table.__name__
