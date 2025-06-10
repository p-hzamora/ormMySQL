from ormlambda.sql import compiler
from .. import default


class SQLiteCompiler(compiler.SQLCompiler):
    render_table_with_column_in_update_from = True
    """Overridden from base SQLCompiler value"""


class SQLiteDDLCompiler(compiler.DDLCompiler): ...


class SQLiteTypeCompiler(compiler.GenericTypeCompiler):
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


class SQLiteDialect(default.DefaultDialect):
    """Details of the SQLite dialect.
    Not used directly in application code.
    """

    name = "mysql"

    statement_compiler = SQLiteCompiler
    ddl_compiler = SQLiteDDLCompiler
    type_compiler_cls = SQLiteTypeCompiler

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
