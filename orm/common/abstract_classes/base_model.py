# region imports
from typing import Type


from orm.common.interfaces import IRepositoryBase, IStatements_two_generic
from orm.databases.my_sql import MySQLStatements, MySQLRepository
from orm.common.abstract_classes import AbstractSQLStatements

from orm.utils import Table


# endregion


class BaseModel[T: Table]:
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
            raise Exception(f"Repository selected does not exits '{repository}'")

        self = object().__new__(cls)
        cls.__init__(self, model, repository)
        return self
