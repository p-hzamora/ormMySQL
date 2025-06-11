from __future__ import annotations
from typing import Any, Type, override, Iterable, Literal, TYPE_CHECKING, Optional
from collections import defaultdict


from ormlambda.repository import BaseRepository
from ormlambda.statements.interfaces import IStatements_two_generic
from ormlambda import Table

from ormlambda.common.errors import AggregateFunctionError

if TYPE_CHECKING:
    from ormlambda.engine.base import Engine
    from ormlambda.dialects.interface.dialect import Dialect
    from ormlambda.sql.clauses import Select


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class BaseStatement[T: Table, TRepo](IStatements_two_generic[T, TRepo]):
    def __init__(self, model: tuple[T, ...], engine: Engine) -> None:
        self._engine = engine
        self._dialect = engine.dialect
        self._query: Optional[str] = None
        self._model: T = model[0] if isinstance(model, Iterable) else model
        self._models: tuple[T] = self._model if isinstance(model, Iterable) else (model,)

        repository = engine.repository
        self.__valid_repository(repository)
        self._repository: BaseRepository[TRepo] = repository

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica
            raise Exception(f"'{model}' class does not inherit from Table class")

    @property
    def dialect(self) -> Dialect:
        return self._dialect

    @override
    def table_exists(self) -> bool:
        return self._repository.table_exists(self._model.__table_name__)

    @staticmethod
    def __valid_repository(repository: Any) -> bool:
        if not isinstance(repository, BaseRepository):
            raise ValueError(f"'repository' attribute does not instance of '{BaseRepository.__name__}'")
        return True

    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    def _return_flavour[TValue](self, query, flavour: Type[TValue], select, **kwargs) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour, select=select, **kwargs)

    def _return_model(self, select, query: str) -> tuple[tuple[T]]:
        response_sql = self._repository.read_sql(query, flavour=dict, select=select)  # store all columns of the SQL query
        if response_sql and isinstance(response_sql, Iterable):
            return ClusterResponse(self._dialect, select, response_sql).cluster()

        return response_sql

    @property
    def query(self) -> str:
        return self._query

    @property
    def model(self) -> Type[T]:
        return self._model

    # TODOL: add *Ts when wil be possible
    @property
    def models(self) -> tuple:
        return self._models

    @property
    def repository(self) -> BaseRepository:
        return self._repository


class ClusterResponse[T]:
    def __init__(self, dialect: Dialect, select: Select[T], response_sql: tuple[dict[str, Any]]) -> None:
        self._dialect: Dialect = dialect
        self._select: Select[T] = select
        self._response_sql: tuple[dict[str, Any]] = response_sql
        self._caster = dialect.caster

    def cluster(self) -> tuple[dict[Type[Table], tuple[Table, ...]]]:
        tbl_dicc: dict[Type[Table], list[dict[str, Any]]] = self._create_cluster()

        response = {}
        tuple_response = []
        # it not depend of flavour attr
        for table, attribute_list in tbl_dicc.items():
            new_instance = []
            for attrs in attribute_list:
                new_instance.append(table(**attrs))
            response[table] = tuple(new_instance)
            tuple_response.append(tuple(new_instance))
        return tuple(tuple_response)

    def _create_cluster(self) -> dict[Type[Table], list[dict[str, Any]]]:
        # We'll create a default list of dicts *once* we know how many rows are in _response_sql
        row_count = len(self._response_sql)

        def make_list_of_dicts() -> list[dict[str, Any]]:
            return [{} for _ in range(row_count)]

        table_attr_dict = defaultdict(make_list_of_dicts)

        for i, dicc_cols in enumerate(self._response_sql):
            for clause in self._select.all_clauses:
                table = clause.table
                col = clause.column

                if col is None or not hasattr(table, col):
                    raise AggregateFunctionError(clause)

                table_attr_dict[table][i][col] = dicc_cols[clause.alias_clause]
        # Convert back to a normal dict if you like (defaultdict is a dict subclass).
        return dict(table_attr_dict)
