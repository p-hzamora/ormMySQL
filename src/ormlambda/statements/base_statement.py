from __future__ import annotations
from typing import Any, Type, override, Iterable, Literal, TYPE_CHECKING, Optional
from collections import defaultdict


from ormlambda.repository import BaseRepository
from ormlambda.statements.interfaces import IStatements
from ormlambda import Table
from ormlambda import util

from ormlambda.common.errors import AggregateFunctionError
from ormlambda.sql.clause_info import IAggregate


if TYPE_CHECKING:
    from ormlambda.engine.base import Engine
    from ormlambda.dialects import Dialect
    from ormlambda.sql.clauses import Select


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class BaseStatement[T: Table](IStatements[T]):
    def __init__(self, model: tuple[T, ...], engine: Engine) -> None:
        self._engine = engine
        self._dialect = engine.dialect
        self._query: Optional[str] = None
        self._model: T = model[0] if isinstance(model, Iterable) else model

        repository = engine.repository
        self.__valid_repository(repository)
        self._repository: BaseRepository = repository

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

    @property
    def query(self) -> str:
        return self._query

    @property
    def model(self) -> Type[T]:
        return self._model

    @property
    def repository(self) -> BaseRepository:
        return self._repository


type ResponseType = Iterable[dict[str, Any]]


class ClusterResponse[T, TFlavour]:
    def __init__(self, select: Select[T], engine: Engine, flavour: TFlavour, query: str) -> None:
        self._select: Select[T] = select
        self.engine = engine
        self.flavour = flavour
        self.query = query

    def cluster(self, response_sql: ResponseType) -> tuple[dict[Type[Table], tuple[Table, ...]]]:
        tbl_dicc: dict[Type[Table], list[dict[str, Any]]] = self._create_cluster(response_sql)

        first_table = list(tbl_dicc)[0]
        tuple_response = []
        # it not depend of flavour attr
        n_attrs = len(tbl_dicc[first_table])
        for i in range(n_attrs):
            new_instance = []
            for table in tbl_dicc:
                attrs = tbl_dicc[table][i]
                new_instance.append(table(**attrs))
            tuple_response.append(tuple(new_instance))
        return tuple(tuple_response)

    def _create_cluster(self, response_sql: ResponseType) -> dict[Type[Table], list[dict[str, Any]]]:
        # We'll create a default list of dicts *once* we know how many rows are in _response_sql
        row_count = len(response_sql)

        def make_list_of_dicts() -> list[dict[str, Any]]:
            return [{} for _ in range(row_count)]

        table_attr_dict = defaultdict(make_list_of_dicts)

        for i, dicc_cols in enumerate(response_sql):
            for clause in self._select.columns:
                # if col is None or not hasattr(table, col):
                if isinstance(clause, IAggregate):
                    raise AggregateFunctionError(clause)

                table = clause.table

                table_attr_dict[table][i][clause.column_name] = dicc_cols[clause.alias]
        # Convert back to a normal dict if you like (defaultdict is a dict subclass).
        return dict(table_attr_dict)

    @util.preload_module("ormlambda.sql.column")
    def response(self, **kwargs) -> TFlavour[T, ...]:
        ColumnProxy = util.preloaded.sql_column.ColumnProxy

        if not self.flavour:
            return self._return_model()

        result = self._return_flavour(self.flavour, self._select, **kwargs)
        if issubclass(self.flavour, tuple) and len(self._select.used_columns()) == 1 and isinstance(self._select.used_columns()[0], ColumnProxy):
            return tuple([x[0] for x in result])
        return result

    def _return_flavour[TValue](self, flavour: Type[TValue], select, **kwargs) -> tuple[TValue]:
        return self.engine.repository.read_sql(self.query, flavour=flavour, select=select, **kwargs)

    def _return_model(self) -> tuple[tuple[T]]:
        response_sql = self.engine.repository.read_sql(self.query, flavour=dict, select=self._select)  # store all columns of the SQL query
        if response_sql and isinstance(response_sql, Iterable):
            response = self.cluster(response_sql)
            if response and len(response[0]) == 1:
                return tuple([x[0] for x in response])
            return response

        return response_sql
