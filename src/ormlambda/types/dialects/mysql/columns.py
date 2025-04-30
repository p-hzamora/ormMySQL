from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from ormlambda.types import DatabaseType

from ...renderers.column_renderer import ColumnDefinitionRenderer
from ...factory import ColumnDefinitionFactory
from ormlambda.caster import Caster

if TYPE_CHECKING:
    from ormlambda import Column


class MySQLColumnDefinitionRenderer(ColumnDefinitionRenderer):
    """MySQL renderer for column definitions"""

    def __init__(self):
        super().__init__()

    def render_definition(self, column: Column, dialect: Optional[DatabaseType] = None) -> str:
        """Render a MySQL column definition"""
        from ormlambda.databases.my_sql.repository import MySQLRepository

        parts = [f"{column.column_name} {column.get_sql_type(dialect)}"]

        # MySQL-specific constraint handling
        if column.is_primary_key:
            parts.append("PRIMARY KEY")

        if column.is_auto_increment:
            parts.append("AUTO_INCREMENT")

        if column.is_unique and not column.is_primary_key:
            parts.append("UNIQUE")

        if column.is_not_null:
            parts.append("NOT NULL")

        if column.default_value is not None:
            value = Caster(MySQLRepository).for_value(column.default_value)
            parts.append(f"DEFAULT {value.from_database}")

        return " ".join(parts)


ColumnDefinitionFactory.register_renderer(DatabaseType.MYSQL, MySQLColumnDefinitionRenderer)
