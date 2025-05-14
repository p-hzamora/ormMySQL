from types import ModuleType
from ormlambda.sql import compiler
from ormlambda import Column
from ormlambda.types.base import DatabaseType
from .. import default

from .types import _NumericType, _StringType


class MySQLCompiler(compiler.SQLCompiler):
    render_table_with_column_in_update_from = True
    """Overridden from base SQLCompiler value"""


class MySQLDDLCompiler(compiler.DDLCompiler):
    def get_column_specification(self, column: Column, **kw) -> str:
        """Builds column DDL."""
        self.dialect.type_compiler_instance.process(column.dtype, **kw)

        return column.get_column_definition(DatabaseType(self.dialect.name))


class MySQLTypeCompiler(compiler.GenericTypeCompiler):
    def _extend_numeric(self, type_: _NumericType, spec: str) -> str:
        "Extend a numeric-type declaration with MySQL specific extensions."

        if type_.unsigned:
            spec += " UNSIGNED"
        if type_.zerofill:
            spec += " ZEROFILL"
        return spec

    def _extend_string(self, type_: _StringType, defaults, spec):
        """Extend a string-type declaration with standard SQL CHARACTER SET /
        COLLATE annotations and MySQL specific extensions.

        """

        def attr(name):
            return getattr(type_, name, defaults.get(name))

        if attr("charset"):
            charset = "CHARACTER SET %s" % attr("charset")
        elif attr("ascii"):
            charset = "ASCII"
        elif attr("unicode"):
            charset = "UNICODE"
        else:
            charset = None

        if attr("collation"):
            collation = "COLLATE %s" % type_.collation
        elif attr("binary"):
            collation = "BINARY"
        else:
            collation = None

        if attr("national"):
            # NATIONAL (aka NCHAR/NVARCHAR) trumps charsets.
            return " ".join([c for c in ("NATIONAL", spec, collation) if c is not None])
        return " ".join([c for c in (spec, charset, collation) if c is not None])

    def visit_INTEGER(self, type_, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                "INTEGER(%(display_width)s)" % {"display_width": type_.display_width},
            )
        else:
            return self._extend_numeric(type_, "INTEGER")

    def visit_VARCHAR(self, type_, **kw):
        if type_.length is None:
            raise ValueError("VARCHAR requires a length on dialect %s" % self.dialect.name)
        return self._extend_string(type_, {}, "VARCHAR(%d)" % type_.length)

    def visit_CHAR(self, type_, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, "CHAR(%(length)s)" % {"length": type_.length})
        else:
            return self._extend_string(type_, {}, "CHAR")


class MySQLDialect(default.DefaultDialect):
    """Details of the MySQL dialect.
    Not used directly in application code.
    """

    name = "mysql"

    statement_compiler = MySQLCompiler
    ddl_compiler = MySQLDDLCompiler
    type_compiler_cls = MySQLTypeCompiler

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from mysql import connector

        return connector
