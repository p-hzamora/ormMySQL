from __future__ import annotations
import abc
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ormlambda.types import SQLType


class SQLTypeRenderer(abc.ABC):
    """Abstract base class defining how to render a SQL type for a specific dialect"""

    @abc.abstractmethod
    def render(self, sql_type: SQLType) -> str:
        """Render the SQL type as a string for a specific dialect"""
        ...

    @classmethod
    def __repr__(cls) -> str:
        return cls.__name__
