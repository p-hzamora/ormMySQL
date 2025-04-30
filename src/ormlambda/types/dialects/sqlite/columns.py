from ormlambda.types.factory import ColumnDefinitionFactory
from typing import Optional
from ormlambda import Column
from ormlambda.types import DatabaseType

from ...renderers.column_renderer import ColumnDefinitionRenderer


class SQLiteColumnDefinitionRenderer(ColumnDefinitionRenderer):
    """SQLite renderer for column definitions"""

    def __init__(self):
        super().__init__()

    def render_definition(self, column: Column, dialect: Optional[DatabaseType] = None) -> str:
        """Render a SQLite column definition"""
        parts = [f"{column.column_name} {column.get_sql_type(dialect)}"]

        # SQLite-specific constraint handling
        # For SQLite, INTEGER PRIMARY KEY automatically becomes an alias for the ROWID
        if column.is_primary_key:
            if not (column.dtype == int and column.is_auto_increment):
                parts.append("PRIMARY KEY")

        if column.is_unique and not column.is_primary_key:
            parts.append("UNIQUE")

        # SQLite doesn't support AUTO_INCREMENT keyword
        # It's handled by INTEGER PRIMARY KEY

        if column.default_value is not None:
            if isinstance(column.default_value, bool):
                # SQLite uses 0/1 for booleans
                parts.append(f"DEFAULT {1 if column.default_value else 0}")
            elif isinstance(column.default_value, str):
                parts.append(f"DEFAULT '{column.default_value}'")
            else:
                parts.append(f"DEFAULT {column.default_value}")

        return " ".join(parts)


ColumnDefinitionFactory.register_renderer(DatabaseType.SQLITE, SQLiteColumnDefinitionRenderer)
