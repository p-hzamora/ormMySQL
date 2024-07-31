# region imports
from typing import Type


from ..interfaces import IRepositoryBase, IStatements
from ...databases.my_sql import MySQLStatements, MySQLRepository
from orm.abstract_model import AbstractSQLStatements

from ...utils import Table


# endregion



class ModelBase[T: Table]:
    """
    Clase base de las clases Model.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """
    statements_dicc: dict[Type[IRepositoryBase], Type[AbstractSQLStatements[T,IRepositoryBase]]] = {
        MySQLRepository: MySQLStatements,
    }

    # region Constructor

    def __new__(cls, model: T, repository: IRepositoryBase) -> IStatements[T]:
        cls:AbstractSQLStatements[T] = cls.statements_dicc.get(type(repository),None)

        if not cls:
            raise Exception(f"Repository selected does not exits '{repository}'")
        
        self = object().__new__(cls)
        cls.__init__(self, model, repository)
        return self
