# region imports
from typing import Type


from ..interfaces import IRepositoryBase, IStatements_two_generic
from ...databases.my_sql import MySQLStatements, MySQLRepository
from orm.abstract_model import AbstractSQLStatements

from ...utils import Table


# endregion


class ModelBase[T: Table]:
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
