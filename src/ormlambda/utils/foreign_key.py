from __future__ import annotations
from typing import Callable, TYPE_CHECKING, Optional, Any, overload

from ormlambda.common.interfaces.IQueryCommand import IQuery


if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.comparer import Comparer
    from ormlambda import Table
    from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


class ForeignKey[TLeft: Table, TRight: Table](IQuery):
    @overload
    def __init__[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None: ...
    @overload
    def __init__[LProp, RProp](self, tright: TRight, relationship: Callable[[TLeft, TRight], Comparer[LProp, RProp]]) -> None: ...

    def __init__[LProp, RProp](
        self,
        tright: Optional[TRight] = None,
        relationship: Optional[Callable[[TLeft, TRight], Comparer[LProp, RProp]]] = None,
        *,
        comparer: Optional[Comparer] = None,
        clause_name: Optional[str] = None,
    ) -> None:
        if comparer is not None and clause_name is not None:
            self.__init__with_comparer(comparer, clause_name)
        else:
            self.__init_with_callable(tright, relationship)

    def __init__with_comparer[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None:
        self._comparer: Comparer[LProp, RProp] = comparer

        self._relationship = None
        self._tleft:TLeft = comparer.left_condition.table
        self._tright: TRight = comparer.right_condition.table
        self._clause_name: str = clause_name

    def __init_with_callable[LProp, RProp](self, tright: Optional[TRight], relationship: Optional[Callable[[TLeft, TRight], Comparer[LProp, RProp]]]) -> None:
        self._tright: TRight = tright
        self._relationship: Callable[[TLeft, TRight], Comparer[LProp, RProp]] = relationship
        self._comparer: Optional[Comparer] = None
        self._tleft: TLeft = None
        self._clause_name: str = None

    def __set_name__(self, owner: TLeft, name) -> None:
        self._tleft: TLeft = owner
        self._clause_name: str = name

    def __get__(self, obj: Optional[TRight], objtype=None) -> ForeignKey | TRight:
        if not obj:
            return self
        return self._tright

    def __set__(self, obj, value):
        raise AttributeError(f"The {ForeignKey.__name__} '{self._clause_name}' in the '{self._tleft.__table_name__}' table cannot be overwritten.")

    def __getattr__(self, name: str):
        return getattr(self._tright, name)

    def __repr__(self) -> str:
        return f"{ForeignKey.__name__}"

    @property
    def query(self) -> str:
        compare = self.resolved_function()
        return f"FOREIGN KEY ({self._tleft.__table_name__}) REFERENCES {compare.right_condition.alias_table}({compare.right_condition._column})"

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        for attr in vars(orig_table):
            if isinstance(attr, ForeignKey):
                clauses.append(attr.query)
        return clauses

    def resolved_function[LProp: Any, RProp: Any](self, context: Optional[ClauseInfoContext] = None) -> Comparer[LProp, RProp]:
        """ """
        if self._comparer is not None:
            return self._comparer

        left = self._tleft
        right = self._tright
        comparer = self._relationship(left, right)
        comparer.set_context(context)
        return comparer
