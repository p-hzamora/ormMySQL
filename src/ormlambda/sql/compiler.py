from __future__ import annotations
from typing import Any, ClassVar, Optional, TYPE_CHECKING

from ormlambda.sql.ddl import CreateColumn
from ormlambda.sql.foreign_key import ForeignKey
from ormlambda.types.base import DatabaseType

from .visitors import Visitor


if TYPE_CHECKING:
    from ormlambda import Column
    from .visitors import Element
    from .elements import ClauseElement
    from ormlambda.sql.type_api import TypeEngine
    from ormlambda.dialects import Dialect
    from ormlambda.sql.ddl import CreateTable
    from .sqltypes import STRING, INTEGER


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
        return type_._compiler_dispatch(self, **kw)


class SQLCompiler(Compiled):
    is_sql = True


class DDLCompiler(Compiled):
    is_ddl = True

    @property
    def sql_compiler(self):
        """Return a SQL compiler that is capable of processing SQL expressions.

        This method returns the SQL compiler for the dialect, which is
        used to process SQL expressions.

        """
        return self.dialect.statement_compiler(self.dialect, None)

    def sqlalchemy_visit_create_table(self, create: CreateTable, **kw):
        table = create.element
        preparer = self.preparer

        text = "\nCREATE "
        if table._prefixes:
            text += " ".join(table._prefixes) + " "

        text += "TABLE "
        if create.if_not_exists:
            text += "IF NOT EXISTS "

        text += preparer.format_table(table) + " "

        create_table_suffix = self.create_table_suffix(table)
        if create_table_suffix:
            text += create_table_suffix + " "

        text += "("

        separator = "\n"

        # if only one primary key, specify it along with the column
        first_pk = False
        for create_column in create.columns:
            column = create_column.element
            try:
                processed = self.process(create_column, first_pk=column.primary_key and not first_pk)
                if processed is not None:
                    text += separator
                    separator = ", \n"
                    text += "\t" + processed
                if column.primary_key:
                    first_pk = True
            except Exception as ce:
                raise ce

        const = self.create_table_constraints(
            table,
            _include_foreign_key_constraints=create.include_foreign_key_constraints,  # noqa
        )
        if const:
            text += separator + "\t" + const

        text += "\n)%s\n\n" % self.post_create_table(table)
        return text

    def visit_create_table(self, create: CreateTable, **kw):
        """Old method to create a table."""
        tablecls = create.element
        column_sql: list[str] = []
        for create_col in create.columns:
            try:
                processed = self.process(create_col)
                if processed is not None:
                    column_sql.append(processed)

            except Exception as ce:
                raise ce

            column_sql.append(create_col.element.get_column_definition(DatabaseType(self.dialect.name)))

        foreign_keys = ForeignKey.create_query(tablecls)
        table_options = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        sql = f"CREATE TABLE {tablecls.__table_name__} (\n\t"
        sql += ",\n\t".join(column_sql)
        sql += "\n\t" if not foreign_keys else ",\n\t"
        sql += ",\n\t".join(foreign_keys)
        sql += f"\n){table_options};"
        return sql

    def visit_create_column(self, create: CreateColumn, first_pk=False, **kw):  # noqa: F821
        column = create.element
        self.dialect.type_compiler_instance
        return self.get_column_specification(column, first_pk=first_pk)

    def get_column_specification(self, column: Column, **kwargs):
        colspec = self.preparer.format_column(column) + " " + self.dialect.type_compiler_cls.process(column.type, type_expression=column)
        default = self.get_column_default_string(column)
        if default is not None:
            colspec += " DEFAULT " + default

        if column.computed is not None:
            colspec += " " + self.process(column.computed)

        if column.identity is not None and self.dialect.supports_identity_columns:
            colspec += " " + self.process(column.identity)

        if not column.nullable and (not column.identity or not self.dialect.supports_identity_columns):
            colspec += " NOT NULL"
        return colspec


class GenericTypeCompiler(TypeCompiler):
    """Generic type compiler

    This class is used to compile ormlambda types into their
    string representations for the given dialect.
    """

    def visit_INTEGER(self, type_: INTEGER, **kw):
        return "INTEGER"

    def _render_string_type(self, type_: STRING, name: str, length_override: Optional[int] = None):
        text = name
        if length_override:
            text += "(%d)" % length_override
        elif type_.length:
            text += "(%d)" % type_.length
        if type_.collation:
            text += ' COLLATE "%s"' % type_.collation
        return text

    def visit_VARCHAR(self, type_: STRING, **kw):
        return self._render_string_type(type_, "VARCHAR")

    def visit_TEXT(self, type_: STRING, **kw):
        return self._render_string_type(type_, "TEXT")

    def visit_integer(self, type_: INTEGER, **kw):
        return self.visit_INTEGER(type_, **kw)

    def visit_string(self, type_: STRING, **kw):
        return self.visit_VARCHAR(type_, **kw)
