from ormlambda.dialects.interface import Dialect
from ormlambda.sql import compiler
from typing import Optional, Any, Type, cast
from types import ModuleType


class DefaultDialect(Dialect):
    """Default implementation of Dialect"""

    statement_compiler = compiler.SQLCompiler
    ddl_compiler = compiler.DDLCompiler
    type_compiler_cls = compiler.GenericTypeCompiler
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

        legacy_tt_callable = getattr(self, "type_compiler", None)
        if legacy_tt_callable is not None:
            tt_callable = cast(
                Type[compiler.GenericTypeCompiler],
                self.type_compiler,
            )
        else:
            tt_callable = self.type_compiler_cls

        self.type_compiler_instance = self.type_compiler = tt_callable(self)
