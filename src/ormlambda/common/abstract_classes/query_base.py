from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

from ormlambda.common.interfaces import IQuery

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.dialects import Dialect


class QueryBase[T: Table](IQuery):
    @property
    @abstractmethod
    def query(self, dialect: Dialect, **kwargs) -> str: ...
