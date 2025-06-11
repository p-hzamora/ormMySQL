from __future__ import annotations
from typing import Callable, TYPE_CHECKING, Optional, Any, Type, cast, overload, ClassVar

from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import Element

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
    from ormlambda.dialects import Dialect


class ForeignKeyContext(set["ForeignKey"]):
    def clear(self):
        to_remove = {x for x in self if not cast(ForeignKey, x)._keep_alive}
        for el in to_remove:
            self.remove(el)

    def remove(self, element):
        return super().remove(element)

    def pop(self, item):
        for el in self:
            if el != item:
                continue

            if not cast(ForeignKey, el)._keep_alive:
                super().remove(el)
            return el

    def add(self, element):
        return super().add(element)


class ForeignKey[TLeft: Table, TRight: Table](Element, IQuery):
    __visit_name__ = "foreign_key"

    stored_calls: ClassVar[ForeignKeyContext] = ForeignKeyContext()

    @overload
    def __new__(self, comparer: Comparer, clause_name: str) -> None: ...
    @overload
    def __new__[TRight](
        cls,
        tright: Type[TRight],
        relationship: Callable[[TLeft, TRight], Any | Comparer],
        keep_alive: bool = ...,
        dialect: Dialect = ...,
    ) -> TRight: ...

    def __new__[TRight](cls, *args, **kwargs) -> TRight:
        return super().__new__(cls)

    def __init__(
        self,
        tright: Optional[TRight] = None,
        relationship: Optional[Callable[[TLeft, TRight], Any | Comparer]] = None,
        *,
        comparer: Optional[Comparer] = None,
        clause_name: Optional[str] = None,
        keep_alive: bool = False,
        **kwargs: Any,
    ) -> None:
        self.kwargs = kwargs
        self._keep_alive = keep_alive
        if comparer is not None and clause_name is not None:
            self.__init__with_comparer(comparer, clause_name, **kwargs)
        else:
            self.__init_with_callable(tright, relationship)

    def __init__with_comparer(self, comparer: Comparer, clause_name: str, **kwargs) -> None:
        self._relationship = None
        self._tleft: TLeft = comparer.left_condition(**kwargs).table
        self._tright: TRight = comparer.right_condition(**kwargs).table
        self._clause_name: str = clause_name
        self._comparer: Comparer = comparer

    def __init_with_callable(self, tright: Optional[TRight], relationship: Optional[Callable[[TLeft, TRight], Comparer]]) -> None:
        self._relationship: Callable[[TLeft, TRight], Comparer] = relationship
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

    def query(self, dialect: Dialect, **kwargs) -> str:
        compare = self.resolved_function(dialect)
        left_col = compare.left_condition(dialect).column
        rcon = alias if (alias := compare.right_condition(dialect).alias_table) else compare.right_condition(dialect).table.__table_name__
        return f"FOREIGN KEY ({left_col}) REFERENCES {rcon}({compare.right_condition(dialect).column})"

    def get_alias(self, dialect: Dialect) -> str:
        self._comparer = self.resolved_function(dialect)
        self._comparer._dialect = dialect
        lcol = self._comparer.left_condition(dialect)._column.column_name
        rcol = self._comparer.right_condition(dialect)._column.column_name
        return f"{self.tleft.__table_name__}_{lcol}_{rcol}"

    @classmethod
    def create_query(cls, orig_table: Table, dialect: Dialect) -> list[str]:
        clauses: list[str] = []

        for attr in orig_table.__dict__.values():
            if isinstance(attr, ForeignKey):
                clauses.append(attr.query(dialect))
        return clauses

    def resolved_function[LProp: Any, RProp: Any](self, dialect: Dialect, context: Optional[ClauseContextType] = None) -> Comparer:
        """ """
        if self._comparer is not None:
            return self._comparer

        left = self._tleft
        right = self._tright
        comparer = self._relationship(left, right)
        comparer.set_context(context)
        comparer._dialect = dialect
        return comparer
