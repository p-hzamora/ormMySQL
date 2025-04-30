from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import abc

if TYPE_CHECKING:
    from ormlambda.types import DatabaseType


class SQLType(abc.ABC):
    """
    Abstract base class for SQL Types.
    This class follows the Strategy pattern by delegating rendering to dialect-specific renderes
    """

    def __init__(self):
        """
        Initialize the SQL type without any dialect-specific logic
        """
        ...

    def get_sql(self, dialect: Optional[DatabaseType] = None) -> str:
        """
        Get the SQL string representation for this type.
        Uses dialect-specific renderer if available.
        """

        from .factory.sql_type_factory import SQLTypeRendererFactory

        renderer = SQLTypeRendererFactory.get_renderer(dialect, type(self))
        return renderer.render(self)
