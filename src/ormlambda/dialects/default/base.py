from ormlambda.dialects.interface import Dialect
from ormlambda.sql import compiler
from typing import Optional, Any
from types import ModuleType
from ormlambda import BaseRepository


class DefaultDialect(Dialect):
    """Default implementation of Dialect"""

    statement_compiler = compiler.SQLCompiler
    ddl_compiler = compiler.DDLCompiler
    type_compiler_cls = compiler.GenericTypeCompiler
    repository_cls = BaseRepository
    default_paramstyle = "named"

    def __init__(
        self,
        dbapi: Optional[ModuleType] = None,  # type: ignore
        **kwargs: Any,
    ):
        self.dbapi = dbapi

        if self.dbapi is not None:
            self.paramstyle = self.dbapi.paramstyle
        else:
            self.paramstyle = self.default_paramstyle
        self.positional = self.paramstyle in (
            "qmark",
            "format",
            "numeric",
            "numeric_dollar",
        )

        tt_callable = self.type_compiler_cls

        self.type_compiler_instance = self.type_compiler = tt_callable(self)

        super().__init__(**kwargs)
