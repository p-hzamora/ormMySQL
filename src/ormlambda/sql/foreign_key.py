from __future__ import annotations
import logging
from typing import Callable, TYPE_CHECKING, Optional, Any, Type, overload

from ormlambda.sql.ddl import BaseDDLElement

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from ormlambda import Table
    from ormlambda.dialects import Dialect

from ormlambda.util import preloaded as _preloaded

log = logging.getLogger(__name__)


class ForeignKey[TLeft: Table, TRight: Table](BaseDDLElement):
    __visit_name__ = "foreign_key"

    __slots__ = (
        "_tright",
        "_relationship",
        "_comparer",
        "_clause_name",
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
        **kwargs: Any,
    ) -> None:
        self.kwargs = kwargs
        if comparer is not None and clause_name is not None:
            self.__init__with_comparer(comparer, clause_name, **kwargs)
        else:
            self.__init_with_callable(tright, relationship)

    def __init__with_comparer(self, comparer: Comparer, clause_name: str, **kwargs) -> None:
        self._relationship = None
        self._tleft: TLeft = comparer.left_condition.table
        self._tright: TRight = comparer.right_condition.table
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

    def get_alias(self, dialect: Dialect) -> str:
        self._comparer = self.resolved_function()
        # TODOH []: look into why i dropped 'lcol' variable
        return f"{self.tleft.__table_name__}_{self.clause_name}"

    @_preloaded.preload_module("ormlambda.sql.table")
    def resolved_function(self) -> Comparer:
        util = _preloaded.sql_table

        if self._comparer is not None:
            return self._comparer

        left = util.TableProxy(self._tleft)
        right = util.TableProxy(self._tright)
        comparer = self._relationship(left, right)
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
