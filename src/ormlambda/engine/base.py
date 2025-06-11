from __future__ import annotations
from typing import TYPE_CHECKING, Literal
from ormlambda.engine import url
from ormlambda.sql.ddl import CreateSchema, DropSchema


if TYPE_CHECKING:
    from ormlambda.dialects import Dialect

type TypeExists = Literal["fail", "replace", "append"]


class Engine:
    def __init__(self, dialect: Dialect, url: url.URL):
        self.dialect = dialect
        self.url = url
        self.repository = self.dialect.repository_cls(url, dialect=dialect)

    def create_schema(self, schema_name: str, if_exists: TypeExists = "fail") -> None:
        if if_exists == "replace":
            self.drop_schema(schema_name, if_exists)

        sql = CreateSchema(schema=schema_name, if_not_exists=if_exists== 'append').compile(self.dialect).string
        try:
            self.repository.execute(sql)
        except Exception:
            if if_exists == "fail":
                raise

    def drop_schema(self, schema_name: str, if_exists: bool = False) -> None:
        """
        Generate a DROP SCHEMA SQL statement for MySQL.

        Args:
            schema_name (str): Name of the schema/database to drop
            if_exists (bool): Whether to include IF EXISTS clause

        Returns:
            str: The SQL DROP SCHEMA statement

        Raises:
            ValueError: If schema_name is empty or contains invalid characters
        """
        # if not schema_name or not isinstance(schema_name, str):
        #     raise ValueError("Schema name must be a non-empty string")

        sql = DropSchema(schema=schema_name, if_exists=if_exists).compile(self.dialect).string
        return self.repository.execute(sql)

    def schema_exists(self, schema: str) -> bool:
        # sql = SchemaExists(schema).compile(self.dialect).string
        # return bool(res and len(res) > 0)

        return self.repository.database_exists(schema)

    def set_database(self, name: str) -> None:
        self.repository.database = name
        return None
