from ...factory.sql_type_factory import SQLTypeRenderer, SQLType
from ...sql_types import (
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
)


class DefaultSQLTypeRenderer(SQLTypeRenderer):
    """Generic fallback renderer"""

    def render(self, sql_type: SQLType) -> str:
        """Generic rendering logic"""

        if isinstance(sql_type, Integer):
            return f"INTEGER{' AUTOINCREMENT' if sql_type.autoincrement else ''}"
        elif isinstance(sql_type, String):
            return f"VARCHAR({sql_type.length})" if sql_type.length else "VARCHAR"
        elif isinstance(sql_type, Text):
            return "TEXT"
        elif isinstance(sql_type, Boolean):
            return "BOOLEAN"
        elif isinstance(sql_type, DateTime):
            return "TIMESTAMP" if sql_type.precision else "DATETIME"
        else:
            return "VARCHAR"  # Default fallback
