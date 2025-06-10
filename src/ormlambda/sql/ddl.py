from __future__ import annotations
from typing import TYPE_CHECKING
from .elements import ClauseElement

if TYPE_CHECKING:
    from ormlambda.dialects.interface.dialect import Dialect
    from ormlambda import Column
    from ormlambda import Table


class BaseDDLElement(ClauseElement):
    """
    Base class for all DDL elements.
    """

    __visit_name__ = "ddl_element"

    def _compiler(self, dialect: Dialect, **kw) -> str:
        """
        Compile the DDL element into a SQL string.
        """
        return dialect.ddl_compiler(dialect, self, **kw)


class CreateTable(BaseDDLElement):
    """
    Class representing a CREATE TABLE statement.
    """

    __visit_name__ = "create_table"

    def __init__(self, element: Table):
        self.element = element
        self.columns = [CreateColumn(c) for c in element.get_columns()]


class CreateColumn[T](BaseDDLElement):
    """
    Class representing a column in a CREATE TABLE statement.
    """

    __visit_name__ = "create_column"

    def __init__(self, element: Column[T]):
        self.element = element


class CreateSchema(BaseDDLElement):
    __visit_name__ = "create_schema"

    def __init__(self, schema: str, if_not_exists: bool = True):
        self.schema: str = schema
        self.if_not_exists: bool = if_not_exists


class DropSchema(BaseDDLElement):
    __visit_name__ = "drop_schema"

    def __init__(self, schema: str, if_exists: bool = True):
        self.schema = schema
        self.if_exists = if_exists


class SchemaExists(BaseDDLElement):
    __visit_name__ = "schema_exists"

    def __init__(self, schema: str):
        self.schema = schema
