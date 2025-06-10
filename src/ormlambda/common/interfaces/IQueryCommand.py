from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class IQuery(ABC):
    """Interface to queries that retrieve any element such as select, limit, offset, where, group by, etc..."""

    @abstractmethod
    def query(self, dialect: Dialect, **kwargs) -> str: ...

    def __repr__(self) -> str:
        return f"{IQuery.__name__}: {self.__class__.__name__}"
