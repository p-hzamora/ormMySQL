from ...renderers.column_renderer import ColumnDefinitionRenderer

from typing import Optional
from ormlambda import Column
from ormlambda.types import DatabaseType

from ormlambda.types.factory.column_definition_factory import ColumnDefinitionFactory


class DefaultColumnDefinitionRenderer(ColumnDefinitionRenderer):
    """Default renderer for column definitions"""

    def __init__(self):
        super().__init__()

    def render_definition(self, column: Column, dialect: Optional[DatabaseType] = None) -> str:
        parts = [f"{column.column_name} {column.get_sql_type(dialect)}"]
        # Add standard constraints
        if column.is_primary_key:
            parts.append("PRIMARY KEY")
        if column.is_auto_increment:
            parts.append("AUTO_INCREMENT")
        if column.is_unique and not column.is_primary_key:
            parts.append("UNIQUE")
        if column.default_value is not None:
            if isinstance(column.default_value, str):
                parts.append(f"DEFAULT '{column.default_value}'")
            else:
                parts.append(f"DEFAULT {column.default_value}")

        return " ".join(parts)


ColumnDefinitionFactory.register_default_renderer(DefaultColumnDefinitionRenderer)
