import abc
import logging
from typing import ClassVar, Type
from ormlambda.types import DatabaseType
from ormlambda import Table, ForeignKey
from ormlambda.utils import __load_module__

log = logging.getLogger(__name__)


class SchemaGenerator(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def create_table(table_class: Type[Table]) -> str:
        """Generate CREATE TABLE statement for the given table class"""
        ...


class SchemaGeneratorFactory:
    _generators: ClassVar[dict[DatabaseType, Type[SchemaGenerator]]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def _initialize(cls):
        if cls._initialized:
            return None

        # # Import column definition renderers
        # try:
        #     __load_module__("..dialects.default.columns", "Default")
        #     __load_module__("..dialects.sqlite.columns", "SQLite")
        #     __load_module__("..dialects.mysql.columns", "MySQL")
        #     __load_module__("..dialects.postgresql.columns", "PostgreSQL")

        #     # Print debug info
        #     log.debug(f"Initialized {SchemaGeneratorFactory.__name__} with:")
        #     log.debug(f"- {len(cls._generators)} dialect-specific renderers")
        #     # log.debug(f"- {cls._default_renderer.__name__} default renderers")

        #     cls._initialized = True

        # except ImportError as e:
        #     log.error(f"Error initializing {SchemaGeneratorFactory.__name__}: {e}")

    @classmethod
    def register_generator(cls, dialect: DatabaseType, generetor_class: Type[SchemaGenerator]) -> None:
        cls._generators[dialect] = generetor_class
        return None

    @classmethod
    def get_generator(cls, dialect: DatabaseType) -> SchemaGenerator:
        """"""
        if not cls._initialized:
            cls._initialize()
        return cls._generators[dialect]()


class MySQLSchemaGenerator(SchemaGenerator):
    """Utility for generating database schema SQL for different dialect"""

    @staticmethod
    def create_table(table_class: Type[Table]) -> str:
        column_sql: list[str] = []
        for column in table_class.get_columns():
            column_sql.append(column.get_column_definition(DatabaseType.MYSQL))

        foreign_keys = ForeignKey.create_query(table_class)
        table_options = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        sql = f"CREATE TABLE {table_class.__table_name__} (\n\t"
        sql += ",\n\t".join(column_sql)
        sql += "\n\t" if not foreign_keys else ",\n\t"
        sql += ",\n\t".join(foreign_keys)
        sql += f"\n){table_options};"
        return sql


class SQLiteSchemaGenerator(SchemaGenerator):
    """Utility for generating SQLite database schema SQL"""

    @staticmethod
    def create_table(table_class: Type[Table]) -> str:
        column_sql: list[str] = []
        for column in table_class.get_columns():
            column_sql.append(column.get_column_definition(DatabaseType.SQLITE))

        foreign_keys = ForeignKey.create_query(table_class)

        # SQLite doesn't use the ENGINE, CHARSET options that MySQL does
        # Instead, you might want to add SQLite-specific pragmas if needed

        sql = f"CREATE TABLE {table_class.__table_name__} (\n\t"
        sql += ",\n\t".join(column_sql)

        # Only add the comma if there are foreign keys
        if foreign_keys:
            sql += ",\n\t"
            sql += "\n\t".join(foreign_keys)

        sql += "\n);"
        return sql

    @staticmethod
    def add_pragmas() -> list[str]:
        """Generate SQLite-specific pragmas for optimal configuration"""
        pragmas = [
            "PRAGMA foreign_keys = ON;",  # Enable foreign key constraints
            "PRAGMA journal_mode = WAL;",  # Use Write-Ahead Logging for better concurrency
            "PRAGMA synchronous = NORMAL;",  # Decent safety with better performance
        ]
        return pragmas

    @staticmethod
    def full_schema(table_classes: list[Type[Table]]) -> str:
        """Generate a complete schema for multiple tables including pragmas"""
        schema_parts = SQLiteSchemaGenerator.add_pragmas()

        # Add all table creation statements
        for table_class in table_classes:
            schema_parts.append(SQLiteSchemaGenerator.create_table(table_class))

        return "\n\n".join(schema_parts)


SchemaGeneratorFactory.register_generator(DatabaseType.MYSQL, MySQLSchemaGenerator)
SchemaGeneratorFactory.register_generator(DatabaseType.SQLITE, SQLiteSchemaGenerator)
