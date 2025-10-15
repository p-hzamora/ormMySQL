from __future__ import annotations
import abc
from typing import Any, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import ColumnProxy
    from ormlambda.sql.types import ColumnType, AliasType


class IFunction[TProp](abc.ABC):
    column: ColumnType[TProp]
    alias: AliasType[TProp]


    def __repr__(self):
            return f"{IFunction.__name__}: {type(self).__name__}"
    

    @abc.abstractmethod
    def used_columns(self) -> Iterable[ColumnProxy]: ...

    @property
    # @abc.abstractmethod
    def dtype(self) -> Any: ...
