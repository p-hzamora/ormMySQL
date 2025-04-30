from ormlambda.types import DatabaseType
from ...factory.sql_type_factory import SQLTypeRenderer, SQLTypeRendererFactory
from ...sql_types import (
    Integer,
    String,
    Char,
    Text,
    Timestamp,
    DateTime,
    Boolean,
)


class SQLiteIntegerRenderer(SQLTypeRenderer):
    """SQLite renderer for Integer type"""

    def render(self, sql_type: Integer) -> str:
        # In SQLite, INTEGER PRIMARY KEY automatically becomes an alias for the ROWID
        # which is automatically assigned a unique integer value
        return "INTEGER"


class SQLiteStringRenderer(SQLTypeRenderer):
    """SQLite renderer for String type"""

    def render(self, sql_type: String) -> str:
        # SQLite's type system is dynamic - length constraints are not enforced
        # but we can include them for documentation purposes
        if sql_type.length:
            return f"VARCHAR({sql_type.length})"
        return "TEXT"


class SQLiteCharRenderer(SQLTypeRenderer):
    """SQLite renderer for Char type"""

    def render(self, sql_type: Char) -> str:
        # SQLite doesn't enforce fixed-length CHAR types
        # but we can include them for documentation purposes
        return f"CHAR({sql_type.length})"


class SQLiteTextRenderer(SQLTypeRenderer):
    """SQLite renderer for Text type"""

    def render(self, sql_type: Text) -> str:
        # SQLite doesn't have text size variations
        return "TEXT"


class SQLiteTimestampRenderer(SQLTypeRenderer):
    """SQLite renderer for Timestamp type"""

    def render(self, sql_type: Timestamp) -> str:
        # SQLite doesn't support timezone or precision specifications
        # in column definitions, but stores TIMESTAMP as text ISO8601 strings
        return "TIMESTAMP"


class SQLiteDateTimeRenderer(SQLTypeRenderer):
    """SQLite renderer for DateTime type"""

    def render(self, sql_type: DateTime) -> str:
        # SQLite doesn't enforce precision for datetime
        return "DATETIME"


class SQLiteBooleanRenderer(SQLTypeRenderer):
    """SQLite renderer for Boolean type"""

    def render(self, sql_type: Boolean) -> str:
        # SQLite doesn't have a native boolean type - uses INTEGER (0/1)
        return "INTEGER"


SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "Integer", SQLiteIntegerRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "String", SQLiteStringRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "Char", SQLiteCharRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "Text", SQLiteTextRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "Timestamp", SQLiteTimestampRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "DateTime", SQLiteDateTimeRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.SQLITE, "Boolean", SQLiteBooleanRenderer)
