from __future__ import annotations
import abc
from typing import ClassVar, Optional, Type, TYPE_CHECKING


if TYPE_CHECKING:
    from ormlambda.caster.caster import Caster
    from ormlambda.repository.interfaces.IRepositoryBase import DBAPIConnection
    from ormlambda.sql.types import DDLCompiler, SQLCompiler, TypeCompiler
    from ormlambda import BaseRepository


class Dialect(abc.ABC):
    """
    Abstract base class for all database dialects.
    """

    dbapi: Optional[DBAPIConnection]
    """A reference to the DBAPI module object itself.

    Ormlambda dialects import DBAPI modules using the classmethod
    :meth:`.Dialect.import_dbapi`. The rationale is so that any dialect
    module can be imported and used to generate SQL statements without the
    need for the actual DBAPI driver to be installed.  Only when an
    :class:`.Engine` is constructed using :func:`.create_engine` does the
    DBAPI get imported; at that point, the creation process will assign
    the DBAPI module to this attribute.

    Dialects should therefore implement :meth:`.Dialect.import_dbapi`
    which will import the necessary module and return it, and then refer
    to ``self.dbapi`` in dialect code in order to refer to the DBAPI module
    contents.

    .. versionchanged:: The :attr:`.Dialect.dbapi` attribute is exclusively
       used as the per-:class:`.Dialect`-instance reference to the DBAPI
       module.   The previous not-fully-documented ``.Dialect.dbapi()``
       classmethod is deprecated and replaced by :meth:`.Dialect.import_dbapi`.

    """

    name: ClassVar[str]
    """The name of the dialect, e.g. 'sqlite', 'postgresql', etc."""
    driver: ClassVar[str]
    """The driver used by the dialect, e.g. 'sqlite3', 'psycopg2', etc."""

    ddl_compiler: ClassVar[Type[DDLCompiler]]
    """The DDL compiler class used by the dialect."""

    statement_compiler: ClassVar[Type[SQLCompiler]]
    """The statement compiler class used by the dialect."""

    type_compiler_cls: ClassVar[Type[TypeCompiler]]
    """The type compiler class used by the dialect."""

    type_compiler_instance: ClassVar[TypeCompiler]
    """The instance of the type compiler class used by the dialect."""

    repository_cls: ClassVar[Type[BaseRepository]]
    """The repository class used by the dialect."""

    caster: ClassVar[Type[Caster]]

    @classmethod
    def get_dialect_cls(cls) -> Type[Dialect]:
        return cls

    @classmethod
    @abc.abstractmethod
    def import_dbapi(cls) -> DBAPIConnection:
        """
        Import the DB API module for the dialect.
        This method should be implemented by subclasses to import the
        appropriate DB API module for the dialect.
        """
        ...

    def __repr__(self):
        return f"{Dialect.__name__}: {type(self).__name__}"
