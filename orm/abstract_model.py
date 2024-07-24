from typing import Literal
from enum import Enum
from collections import defaultdict

from orm.utils import Table
from orm.interfaces import IQuery, IStatements, IRepositoryBase

OrderType = Literal["ASC", "DESC"]


class JoinType(Enum):
    RIGHT_INCLUSIVE = "RIGHT JOIN"
    LEFT_INCLUSIVE = "LEFT JOIN"
    RIGHT_EXCLUSIVE = "RIGHT JOIN"
    LEFT_EXCLUSIVE = "LEFT JOIN"
    FULL_OUTER_INCLUSIVE = "RIGHT JOIN"
    FULL_OUTER_EXCLUSIVE = "RIGHT JOIN"
    INNER_JOIN = "INNER JOIN"


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "with_recursive", "limit", "offset"]


class AbstractSQLStatements[T: Table](IStatements[T]):
    __slots__ = ("_model", "_repository", "_query_list")
    __order__: tuple[ORDER_QUERIES] = ("select", "join", "where", "order", "with", "with_recursive", "limit", "offset")

    def __init__(self, model: T, repository: IRepositoryBase) -> None:
        self._model: T = model
        self._repository: IRepositoryBase = repository
        self._query_list: dict[ORDER_QUERIES, list[IQuery]] = defaultdict(list)

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica

            raise Exception(f"'{model}' class does not inherit from Table class")

        if model.__table_name__ is Ellipsis:
            raise Exception(f"class variable '__table_name__' must be declared in '{model.__name__}' class")
