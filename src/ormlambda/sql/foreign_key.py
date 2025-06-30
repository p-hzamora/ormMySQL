from __future__ import annotations
import logging
from typing import Callable, TYPE_CHECKING, Optional, Any, Type, overload, ClassVar

from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.elements import Element
from ormlambda.sql.context import PATH_CONTEXT

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from ormlambda import Table
    from ormlambda.dialects import Dialect
    from ormlambda.sql.context import FKChain

log = logging.getLogger(__name__)


class ForeignKey[TLeft: Table, TRight: Table](Element, IQuery):
    __visit_name__ = "foreign_key"

    __slots__ = (
        "_tright",
        "_relationship",
        "_comparer",
        "_clause_name",
        "_keep_alive",
    )

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

        self._path: Optional[FKChain] = None

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
        if obj:
            return self.tright

        current_path = PATH_CONTEXT.get_current_path()

        # Reset CONTEXT when we detect that base table is the same at left table in ForeignKey class and .steps is filled
        if not current_path.base or (current_path.base == self.tleft and len(current_path.steps) > 0):
            PATH_CONTEXT.reset_current_path(self.tleft)

            # update PATH_CONTEXT with a new initialization like we'll do on PATH_CONTEXT.query_context(self.tleft) in with statement
            current_path = PATH_CONTEXT.get_current_path()
        if not current_path:
            log.critical(f"{ForeignKey.__name__} '{self._clause_name}' accessed outside of path context. Must be used within a query context.")
            return self

        new_path = current_path.copy()
        new_path.add_step(self)

        PATH_CONTEXT.add_foreign_key_access(self, new_path)
        PATH_CONTEXT.set_current_path(new_path)
        
        self._path = new_path
        return self

    def __set__(self, obj, value):
        raise AttributeError(f"The {ForeignKey.__name__} '{self._clause_name}' in the '{self._tleft.__table_name__}' table cannot be overwritten.")

    def __getattr__(self, name: str):
        if self._tright is None:
            raise AttributeError("No right table assigned to ForeignKey")
        return getattr(self._tright, name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self._tleft.__name__ if self._tleft else 'None'}, right={self._tright.__name__ if self._tright else 'None'}, name={self._clause_name})"

    @property
    def tleft(self) -> Table:
        return self._tleft

    @property
    def tright(self) -> Table:
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
        return f"{self.tleft.__table_name__}_{lcol}_{self.clause_name}"

    @classmethod
    def create_query(cls, orig_table: Table, dialect: Dialect) -> list[str]:
        clauses: list[str] = []

        for attr in orig_table.__dict__.values():
            if isinstance(attr, ForeignKey):
                clauses.append(attr.query(dialect))
        return clauses

    def resolved_function[LProp: Any, RProp: Any](self, dialect: Dialect) -> Comparer:
        """ """
        if self._comparer is not None:
            return self._comparer

        left = self._tleft
        right = self._tright
        comparer = self._relationship(left, right)
        comparer._dialect = dialect
        return comparer

    def __hash__(self):
        return hash(
            (
                self._tleft,
                self._tright,
                self._clause_name,
            )
        )

    def __eq__(self, other: ForeignKey):
        return hash(other) == hash(self)
