import abc
from typing import Optional
from ormlambda import Column
from ormlambda.types import DatabaseType


class ColumnDefinitionRenderer(abc.ABC):
    """Abstract base class for rendering column definitions"""
    @abc.abstractmethod
    def render_definition(self, column: Column, dialect: Optional[DatabaseType]) -> str: 
        """Render the complete column definition SQL"""
        ...
