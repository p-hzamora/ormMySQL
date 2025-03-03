from __future__ import annotations

from ormlambda.sql import Table
from ormlambda.repository import IRepositoryBase
from ormlambda.statements.interfaces import IStatements_two_generic
from ormlambda.statements import BaseStatement
from ..databases.my_sql import MySQLStatements, MySQLRepository


from typing import Optional, Type, TYPE_CHECKING, Callable, overload

from ormlambda.common.global_checker import GlobalChecker
from ormlambda.sql.types import ColumnType
from ormlambda.engine.template import RepositoryTemplateDict

if TYPE_CHECKING:
    from ormlambda.caster import BaseCaster
    from ormlambda.repository import IRepositoryBase
    from ormlambda.repository import BaseRepository
    from ormlambda.databases.my_sql import MySQLRepository


# endregion


class BaseModel[T: Type[Table], TRepo](IStatements_two_generic[T, TRepo]):
    """
    Class to select the correct BaseStatement class depends on the repository.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    statements_dicc: dict[Type[IRepositoryBase], Type[BaseStatement[T, IRepositoryBase]]] = {
        MySQLRepository: MySQLStatements,
    }

    # region Constructor

    def __new__[TRepo](cls, model: tuple[T], repository: IRepositoryBase) -> IStatements_two_generic[T, TRepo]:
        if repository is None:
            raise ValueError("`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class")
        cls: Type[BaseStatement[T, TRepo]] = RepositoryTemplateDict[TRepo]().get(repository).statement

        if not cls:
            raise Exception(f"The selected repository '{repository}' does not exist.")

        self = object().__new__(cls)
        cls.__init__(self, model, repository)
        return self
