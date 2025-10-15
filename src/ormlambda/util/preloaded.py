from typing import Callable, TYPE_CHECKING
import importlib

type FuncType[T] = Callable[..., T]


if TYPE_CHECKING:
    from ormlambda.sql import table as _sql_table
    from ormlambda.sql import column as _sql_column
    from ormlambda.sql import comparer as _sql_comparer
    from ormlambda.sql import column_table_proxy as _sql_column_table_proxy
    from ormlambda.sql import foreign_key as _sql_foreign_key
    from ormlambda.sql import clause_info as _sql_clause_info
    from ormlambda.sql import sqltypes as _sql_sqltypes
    from ormlambda.sql import clauses as _sql_clauses
    from ormlambda.sql import type_api as _sql_type_api
    from ormlambda.sql import functions as _sql_functions

    sql_column = _sql_column
    sql_table = _sql_table
    sql_comparer = _sql_comparer
    sql_column_table_proxy = _sql_column_table_proxy
    sql_foreign_key = _sql_foreign_key
    sql_clause_info = _sql_clause_info
    sql_types = _sql_sqltypes
    sql_clauses = _sql_clauses
    sql_functions = _sql_functions

    sql_type_api = _sql_type_api

class ModuleRegistry:
    """Registry of modules to load in a package init file.

    To avoid potential thread safety issues for imports that are deferred
    in a function, like https://bugs.python.org/issue38884, these modules
    are added to the system module cache by importing them after the packages
    has finished initialization.

    A global instance is provided under the name :attr:`.preloaded`. Use
    the function :func:`.preload_module` to register modules to load and
    :meth:`.import_prefix` to load all the modules that start with the
    given path.

    While the modules are loaded in the global module cache, it's advisable
    to access them using :attr:`.preloaded` to ensure that it was actually
    registered. Each registered module is added to the instance ``__dict__``
    in the form `<package>_<module>`, omitting ``sqlalchemy`` from the package
    name. Example: ``sqlalchemy.sql.util`` becomes ``preloaded.sql_util``.
    """

    def __init__(self, prefix="ormlambda."):
        self.module_registry: set[str] = set()
        self.prefix: str = prefix

    def preload_module[T, **P](self, *deps: str) -> Callable[P, T]:
        """Adds the specified modules to the list to load.

        This method can be used both as a normal function and as a decorator.
        No change is performed to the decorated object.
        """
        self.module_registry.update(deps)
        return lambda fn: fn

    def import_prefix(self, path: str) -> None:
        """Resolve all the modules in the registry that start with the
        specified path.
        """
        for module in self.module_registry:
            if self.prefix:
                key = module.split(self.prefix)[-1].replace(".", "_")
            else:
                key = module

            if (not path or module.startswith(path)) and key not in self.__dict__:
                _module = importlib.import_module(module)
                self.__dict__[key] = globals()[key] = _module
        return None


_reg = ModuleRegistry()
preload_module = _reg.preload_module
import_prefix = _reg.import_prefix
