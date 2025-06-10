from types import ModuleType
from ..default import DefaultDialect
from ormlambda.sql import compiler


class SQLiteCompiler(compiler.SQLCompiler): ...


class SQLiteDDLCompiler(compiler.DDLCompiler): ...


class SQLiteTypeCompiler(compiler.TypeCompiler): ...


class SQLiteDialect_pysqlite(DefaultDialect):
    name = "sqlite"

    statement_compiler = SQLiteCompiler
    ddl_compiler = SQLiteDDLCompiler
    type_compiler_cls = SQLiteTypeCompiler

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from sqlite3 import dbapi2 as sqlite

        return sqlite


dialect = SQLiteDialect_pysqlite
