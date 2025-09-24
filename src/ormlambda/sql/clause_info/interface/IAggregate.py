from __future__ import annotations
import abc
from typing import Any, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import ColumnProxy
from ormlambda.common.interfaces.IQueryCommand import IQuery


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...

    def __repr__(self):
        return f"{IAggregate.__name__}: {type(self).__name__}"

    # @abc.abstractmethod
    def used_columns(self) -> Iterable[ColumnProxy]: ...

    @property
    @abc.abstractmethod
    def dtype(self) -> Any: ...
