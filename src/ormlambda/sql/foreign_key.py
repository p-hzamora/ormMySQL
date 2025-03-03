from __future__ import annotations
from typing import Callable, TYPE_CHECKING, Optional, Any, Type, overload

from ormlambda.common.interfaces.IQueryCommand import IQuery


if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType


class ForeignKey[TLeft: Table, TRight: Table](IQuery):
    stored_calls: set[ForeignKey] = set()

    @overload
    def __new__[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None: ...
    @overload
    def __new__[LProp, TRight, RProp](cls, tright: Type[TRight], relationship: Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]]) -> TRight: ...

    def __new__[LProp, TRight, RProp](cls, tright: Optional[TRight] = None, relationship: Optional[Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]]] = None, *, comparer: Optional[Comparer] = None, clause_name: Optional[str] = None) -> TRight:
        return super().__new__(cls)

    def __init__[LProp, RProp](
        self,
        tright: Optional[TRight] = None,
        relationship: Optional[Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]]] = None,
        *,
        comparer: Optional[Comparer] = None,
        clause_name: Optional[str] = None,
    ) -> None:
        if comparer is not None and clause_name is not None:
            self.__init__with_comparer(comparer, clause_name)
        else:
            self.__init_with_callable(tright, relationship)

    def __init__with_comparer[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None:
        self._relationship = None
        self._tleft: TLeft = comparer.left_condition.table
        self._tright: TRight = comparer.right_condition.table
        self._clause_name: str = clause_name
        self._comparer: Comparer[LProp, RProp] = comparer

    def __init_with_callable[LProp, RProp](self, tright: Optional[TRight], relationship: Optional[Callable[[TLeft, TRight], Comparer[LProp, RProp]]]) -> None:
        self._relationship: Callable[[TLeft, TRight], Comparer[LProp, RProp]] = relationship
        self._tleft: TLeft = None
        self._tright: TRight = tright
        self._clause_name: str = None
        self._comparer: Optional[Comparer] = None

    def __set_name__(self, owner: TLeft, name) -> None:
        self._tleft: TLeft = owner
        self._clause_name: str = name

    def __get__(self, obj: Optional[TRight], objtype=None) -> ForeignKey[TLeft, TRight] | TRight:
        if not obj:
            ForeignKey.stored_calls.add(self)
            return self
        return self._tright

    def __set__(self, obj, value):
        raise AttributeError(f"The {ForeignKey.__name__} '{self._clause_name}' in the '{self._tleft.__table_name__}' table cannot be overwritten.")

    def __getattr__(self, name: str):
        if self._tright is None:
            raise AttributeError("No right table assigned to ForeignKey")
        return getattr(self._tright, name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" f"left={self._tleft.__name__ if self._tleft else 'None'}, " f"right={self._tright.__name__ if self._tright else 'None'}, " f"name={self._clause_name})"

    @property
    def tleft(self) -> TLeft:
        return self._tleft

    @property
    def tright(self) -> TRight:
        return self._tright

    @property
    def clause_name(self) -> str:
        return self._clause_name

    @property
    def query(self) -> str:
        compare = self.resolved_function()
        rcon = alias if (alias := compare.right_condition.alias_table) else compare.right_condition.table.__table_name__
        return f"FOREIGN KEY ({self._tleft.__table_name__}) REFERENCES {rcon}({compare.right_condition._column.column_name})"

    @property
    def alias(self) -> str:
        self._comparer = self.resolved_function()
        lcol = self._comparer.left_condition._column.column_name
        rcol = self._comparer.right_condition._column.column_name
        return f"{self.tleft.__table_name__}_{lcol}_{rcol}"

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        for attr in vars(orig_table):
            if isinstance(attr, ForeignKey):
                clauses.append(attr.query)
        return clauses

    def resolved_function[LProp: Any, RProp: Any](self, context: ClauseContextType = None) -> Comparer[LProp, RProp]:
        """ """
        if self._comparer is not None:
            return self._comparer

        left = self._tleft
        right = self._tright
        comparer = self._relationship(left, right)
        comparer.set_context(context)
        return comparer
