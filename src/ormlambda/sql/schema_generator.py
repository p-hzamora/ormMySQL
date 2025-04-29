from typing import Type
from ormlambda.types import DatabaseType
from src.ormlambda.sql.table.table_constructor import Table


class SchemaGenerator:
    """Utility for generating database schema SQL for different dialect"""

    def __init__(self, dialect: DatabaseType):
        self.dialect = dialect

    def create_table(self, table_class: Type[Table]) -> str:
        """Generate CREATE TABLE statement for the given table class"""
        column_sql = []
        for str_column in table_class.get_columns():
            column = table_class.get_column(str_column)
            column_sql.append(column.get_column_definition(self.dialect))

        table_options = ""
        if self.dialect == DatabaseType.MYSQL:
            table_options = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        sql = f"CREATE TABLE {table_class.__table_name__} (\n\t)"
        sql += ",\n\t".join(column_sql)
        sql += f"\n){table_options};"
        return sql
