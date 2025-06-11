from __future__ import annotations
import abc
from typing import Any, ClassVar, Optional, TYPE_CHECKING

from ormlambda.sql.ddl import CreateColumn
from ormlambda.sql.foreign_key import ForeignKey
from ormlambda.sql.sqltypes import resolve_primitive_types

from .visitors import Visitor
from ormlambda import util
from ormlambda.sql.type_api import TypeEngine

if TYPE_CHECKING:
    from ormlambda import Column
    from .visitors import Element
    from .elements import ClauseElement
    from ormlambda.dialects import Dialect
    from ormlambda.sql.ddl import CreateTable, CreateSchema, DropSchema
    from .sqltypes import (
        INTEGER,
        SMALLINTEGER,
        BIGINTEGER,
        NUMERIC,
        FLOAT,
        REAL,
        DOUBLE,
        STRING,
        TEXT,
        UNICODE,
        UNICODETEXT,
        NCHAR,
        VARCHAR,
        NVARCHAR,
        CHAR,
        DATE,
        TIME,
        DATETIME,
        TIMESTAMP,
        BOOLEAN,
        LARGEBINARY,
        VARBINARY,
        ENUM,
        POINT,
    )

    from ormlambda.sql.clauses import (
        Insert,
        Delete,
        Upsert,
        Update,
        Limit,
        Offset,
        Count,
        Where,
        Having,
        Order,
        Concat,
        Max,
        Min,
        Sum,
        Groupby,
    )


class Compiled:
    """Represent a compiled SQL or DDL expression.

    The ``__str__`` method of the ``Compiled`` object should produce
    the actual text of the statement.  ``Compiled`` objects are
    specific to their underlying database dialect, and also may
    or may not be specific to the columns referenced within a
    particular set of bind parameters.  In no case should the
    ``Compiled`` object be dependent on the actual values of those
    bind parameters, even though it may reference those values as
    defaults.
    """

    dialect: Dialect
    "The dialect to compile against."

    statement: Optional[ClauseElement] = None
    "The statement to compile."

    string: str = ""
    "The string representation of the ``statement``"

    _gen_time: float
    "The time when the statement was generated."

    is_sql: ClassVar[bool] = False
    is_ddl: ClassVar[bool] = False

    def __init__(
        self,
        dialect: Dialect,
        statement: Optional[ClauseElement] = None,
        **kw: Any,
    ) -> None:
        """Construct a new :class:`.Compiled` object.

        :param dialect: :class:`.Dialect` to compile against.

        :param statement: :class:`_expression.ClauseElement` to be compiled.

        """
        self.dialect = dialect

        if statement is not None:
            self.statement = statement
        self.string = self.process(self.statement, **kw)

    @property
    def sql_compiler(self):
        """Return a Compiled that is capable of processing SQL expressions.

        If this compiler is one, it would likely just return 'self'.

        """

        raise NotImplementedError()

    def process(self, obj: Element, **kwargs: Any) -> str:
        return obj._compiler_dispatch(self, **kwargs)


class TypeCompiler(Visitor):
    """Base class for all type compilers."""

    def __init__(self, dialect: Dialect):
        self.dialect = dialect

    def process(self, type_: TypeEngine[Any], **kw: Any) -> str:
        """Process a type object into a string representation.

        :param type_: The type object to process.
        :param kw: Additional keyword arguments.
        :return: The string representation of the type object.
        """
        if not isinstance(type_, TypeEngine):
            type_ = resolve_primitive_types(type_)
        return type_._compiler_dispatch(self, **kw)


class SQLCompiler(Compiled, abc.ABC):
    is_sql = True

    @abc.abstractmethod
    def visit_insert(self, insert: Insert, **kw) -> Insert: ...
    @abc.abstractmethod
    def visit_delete(self, delete: Delete, **kw) -> Delete: ...
    @abc.abstractmethod
    def visit_upsert(self, upsert: Upsert, **kw) -> Upsert: ...
    @abc.abstractmethod
    def visit_update(self, update: Update, **kw) -> Update: ...
    @abc.abstractmethod
    def visit_limit(self, limit: Limit, **kw) -> Limit: ...
    @abc.abstractmethod
    def visit_offset(self, offset: Offset, **kw) -> Offset: ...
    @abc.abstractmethod
    def visit_count(self, count: Count, **kw) -> Count: ...
    @abc.abstractmethod
    def visit_where(self, where: Where, **kw) -> Where: ...
    @abc.abstractmethod
    def visit_having(self, having: Having, **kw) -> Having: ...
    @abc.abstractmethod
    def visit_order(self, order: Order, **kw) -> Order: ...
    @abc.abstractmethod
    def visit_concat(self, concat: Concat, **kw) -> Concat: ...
    @abc.abstractmethod
    def visit_max(self, max: Max, **kw) -> Max: ...
    @abc.abstractmethod
    def visit_min(self, min: Min, **kw) -> Min: ...
    @abc.abstractmethod
    def visit_sum(self, sum: Sum, **kw) -> Sum: ...
    @abc.abstractmethod
    def visit_group_by(self, groupby: Groupby, **kw) -> Groupby: ...


class DDLCompiler(Compiled):
    is_ddl = True

    if TYPE_CHECKING:

        def __init__(
            self,
            dialect: Dialect,
            statement: Optional[ClauseElement] = None,
            **kw: Any,
        ) -> None: ...

    @property
    def sql_compiler(self):
        """Return a SQL compiler that is capable of processing SQL expressions.

        This method returns the SQL compiler for the dialect, which is
        used to process SQL expressions.

        """
        return self.dialect.statement_compiler(self.dialect, None)

    def visit_create_schema(self, create: CreateSchema, **kw) -> str:
        """
        Generate a CREATE SCHEMA SQL statement for MySQL.

        Args:
            schema_name (str): Name of the schema/database to create
            if_not_exists (bool): Whether to include IF NOT EXISTS clause

        Returns:
            str: The SQL CREATE SCHEMA statement

        Raises:
            ValueError: If schema_name is empty or contains invalid characters
        """
        schema_name = create.schema

        util.avoid_sql_injection(schema_name)

        if_not_exists_clause = "IF NOT EXISTS " if create.if_not_exists else ""
        return f"CREATE SCHEMA {if_not_exists_clause}{schema_name};"

    def visit_drop_schema(self, drop: DropSchema, **kw):
        if_exists_clause = "IF EXISTS " if drop.if_exists else ""
        return f"DROP SCHEMA {if_exists_clause}{drop.schema};"

    def visit_schema_exists(self, schema: str) -> bool:
        return f"SHOW DATABASES LIKE {schema};"
        # return f"SHOW DATABASES LIKE {self.dialect.caster.PLACEHOLDER};", (schema,)

    def visit_create_table(self, create: CreateTable, **kw) -> str:
        tablecls = create.element
        column_sql: list[str] = []
        for create_col in create.columns:
            try:
                processed = self.process(create_col)
                if processed is not None:
                    column_sql.append(processed)

            except Exception:
                raise

        foreign_keys = ForeignKey.create_query(tablecls, self.dialect)
        table_options = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        sql = f"CREATE TABLE {tablecls.__table_name__} (\n\t"
        sql += ",\n\t".join(column_sql)
        sql += "\n\t" if not foreign_keys else ",\n\t"
        sql += ",\n\t".join(foreign_keys)
        sql += f"\n){table_options};"
        return sql

    def visit_create_column(self, create: CreateColumn, first_pk=False, **kw):  # noqa: F821
        column = create.element
        return self.get_column_specification(column)

    def get_column_specification(self, column: Column, **kwargs):
        colspec = column.column_name + " " + self.dialect.type_compiler_instance.process(column.dtype)
        default = self.get_column_default_string(column)
        if default is not None:
            colspec += " DEFAULT " + default

        if column.is_not_null:
            colspec += " NOT NULL"

        if column.is_primary_key:
            colspec += " PRIMARY KEY"
        return colspec

    def get_column_default_string(self, column: Column) -> Optional[str]:
        if isinstance(column.default_value, str):
            return column.default_value
        if not column.default_value:
            return None
        return None


class GenericTypeCompiler(TypeCompiler):
    """Generic type compiler

    This class is used to compile ormlambda types into their
    string representations for the given dialect.
    """

    def _render_string_type(self, type_: STRING, name: str, length_override: Optional[int] = None):
        text = name
        if length_override:
            text += "(%d)" % length_override
        elif type_.length:
            text += "(%d)" % type_.length
        if type_.collation:
            text += ' COLLATE "%s"' % type_.collation
        return text

    def visit_INTEGER(self, type_: INTEGER, **kw):
        return "INTEGER"

    def visit_SMALLINTEGER(self, type_: SMALLINTEGER, **kw):
        return "SMALLINTEGER"

    def visit_BIGINTEGER(self, type_: BIGINTEGER, **kw):
        return "BIGINTEGER"

    def visit_NUMERIC(self, type_: NUMERIC, **kw):
        return "NUMERIC"

    def visit_FLOAT(self, type_: FLOAT, **kw):
        return "FLOAT"

    def visit_REAL(self, type_: REAL, **kw):
        return "REAL"

    def visit_DOUBLE(self, type_: DOUBLE, **kw):
        return "DOUBLE"

    def visit_TEXT(self, type_: TEXT, **kw):
        return self._render_string_type(type_, "TEXT", **kw)

    def visit_UNICODE(self, type_: UNICODE, **kw):
        return self._render_string_type(type_, "UNICODE", **kw)

    def visit_UNICODETEXT(self, type_: UNICODETEXT, **kw):
        return self._render_string_type(type_, "UNICODETEXT", **kw)

    def visit_CHAR(self, type_: CHAR, **kw):
        return self._render_string_type(type_, "CHAR", **kw)

    def visit_NCHAR(self, type_: NCHAR, **kw):
        return self._render_string_type(type_, "NCHAR", **kw)

    def visit_VARCHAR(self, type_: VARCHAR, **kw):
        return self._render_string_type(type_, "VARCHAR", **kw)

    def visit_NVARCHAR(self, type_: NVARCHAR, **kw):
        return self._render_string_type(type_, "NVARCHAR", **kw)

    def visit_DATE(self, type_: DATE, **kw):
        return "DATE"

    def visit_TIME(self, type_: TIME, **kw):
        return "TIME"

    def visit_DATETIME(self, type_: DATETIME, **kw):
        return "DATETIME"

    def visit_TIMESTAMP(self, type_: TIMESTAMP, **kw):
        return "TIMESTAMP"

    def visit_BOOLEAN(self, type_: BOOLEAN, **kw):
        return "BOOLEAN"

    def visit_LARGEBINARY(self, type_: LARGEBINARY, **kw):
        return "LARGEBINARY"

    def visit_VARBINARY(self, type_: VARBINARY, **kw):
        return "VARBINARY"

    def visit_ENUM(self, type_: ENUM, **kw):
        return "ENUM"

    def visit_BLOB(self, type_: LARGEBINARY, **kw):
        return "BLOB"

    def visit_null(self, type_: POINT, **kw):
        return "NULL"

    def visit_POINT(self, _type: POINT, **kw):
        return "POINT"

    def visit_uuid(self, type_, **kw):
        if not type_.native_uuid or not self.dialect.supports_native_uuid:
            return self._render_string_type(type_, "CHAR", length_override=32)
        else:
            return self.visit_UUID(type_, **kw)

    def visit_large_binary(self, type_, **kw):
        return self.visit_BLOB(type_, **kw)

    def visit_boolean(self, type_, **kw):
        return self.visit_BOOLEAN(type_, **kw)

    def visit_time(self, type_, **kw):
        return self.visit_TIME(type_, **kw)

    def visit_datetime(self, type_, **kw):
        return self.visit_DATETIME(type_, **kw)

    def visit_date(self, type_, **kw):
        return self.visit_DATE(type_, **kw)

    def visit_big_integer(self, type_, **kw):
        return self.visit_BIGINT(type_, **kw)

    def visit_small_integer(self, type_, **kw):
        return self.visit_SMALLINT(type_, **kw)

    def visit_integer(self, type_, **kw):
        return self.visit_INTEGER(type_, **kw)

    def visit_real(self, type_, **kw):
        return self.visit_REAL(type_, **kw)

    def visit_float(self, type_, **kw):
        return self.visit_FLOAT(type_, **kw)

    def visit_double(self, type_, **kw):
        return self.visit_DOUBLE(type_, **kw)

    def visit_numeric(self, type_, **kw):
        return self.visit_NUMERIC(type_, **kw)

    def visit_string(self, type_, **kw):
        return self.visit_VARCHAR(type_, **kw)

    def visit_unicode(self, type_, **kw):
        return self.visit_VARCHAR(type_, **kw)

    def visit_text(self, type_, **kw):
        return self.visit_TEXT(type_, **kw)

    def visit_unicode_text(self, type_, **kw):
        return self.visit_TEXT(type_, **kw)

    def visit_enum(self, type_, **kw):
        return self.visit_VARCHAR(type_, **kw)

    def visit_point(self, type_: POINT, **kw):
        return self.visit_POINT(type_, **kw)
