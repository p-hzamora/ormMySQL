from typing import Type


from .utils import Table
from .common.interfaces import IRepositoryBase, IStatements_two_generic
from .common.abstract_classes import AbstractSQLStatements
from .databases.my_sql import MySQLStatements, MySQLRepository


# endregion


class BaseModel[T: Type[Table]]:
    """
    Class to select the correct AbstractSQLStatements class depends on the repository.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    statements_dicc: dict[Type[IRepositoryBase], Type[AbstractSQLStatements[T, IRepositoryBase]]] = {
        MySQLRepository: MySQLStatements,
    }

    # region Constructor

    def __new__[TRepo](cls, model: T, repository: IRepositoryBase[TRepo]) -> IStatements_two_generic[T, TRepo]:
        cls: AbstractSQLStatements[T, TRepo] = cls.statements_dicc.get(type(repository), None)

        if not cls:
            raise Exception(f"The selected repository '{repository}' does not exist.")

        self = object().__new__(cls)
        cls.__init__(self, model, repository)
        return self
