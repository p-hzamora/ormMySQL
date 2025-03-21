from __future__ import annotations
from typing import Any, Type, override, Iterable, Literal, TYPE_CHECKING, Optional
from collections import defaultdict


from ormlambda.repository import BaseRepository
from ormlambda.statements.interfaces import IStatements_two_generic
from ormlambda import Table

from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.caster.caster import Caster


if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
    from ormlambda.sql.clause_info import ClauseInfo


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class BaseStatement[T: Table, TRepo](IStatements_two_generic[T, TRepo]):
    def __init__(self, model: tuple[T], repository: BaseRepository) -> None:
        self.__valid_repository(repository)

        self._query: Optional[str] = None
        self._model: T = model[0] if isinstance(model, Iterable) else model
        self._models: tuple[T] = self._model if isinstance(model, Iterable) else (model,)
        self._repository: BaseRepository = repository

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica
            raise Exception(f"'{model}' class does not inherit from Table class")

    @staticmethod
    def __valid_repository(repository: Any) -> bool:
        if not isinstance(repository, BaseRepository):
            raise ValueError(f"'repository' attribute does not instance of '{BaseRepository.__name__}'")
        return True

    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    def _return_flavour[TValue](self, query, flavour: Type[TValue], select, **kwargs) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour, model=self._model, select=select, **kwargs)

    def _return_model(self, select, query: str) -> tuple[tuple[T]]:
        response_sql = self._repository.read_sql(query, flavour=dict, model=self._model, select=select)  # store all columns of the SQL query

        if response_sql and isinstance(response_sql, Iterable):
            return ClusterQuery(self.repository, select, response_sql).clean_response()

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
    @override
    def repository(self) -> BaseRepository: ...


class ClusterQuery[T]:
    def __init__(self, repository: BaseRepository, select: DecompositionQueryBase[T], response_sql: tuple[dict[str, Any]]) -> None:
        self._repository: BaseRepository = repository
        self._select: DecompositionQueryBase[T] = select
        self._response_sql: tuple[dict[str, Any]] = response_sql
        self._caster = Caster(repository)

    def clean_response(self) -> tuple[dict[Type[Table], tuple[Table, ...]]]:
        tbl_dicc: dict[Type[Table], list[dict[str, Any]]] = self.__loop_foo()

        response = {}
        tuple_response = []
        # it not depend of flavour attr
        for table, attribute_list in tbl_dicc.items():
            new_instance = []
            for attrs in attribute_list:
                casted_attr = {key: self._caster.for_value(value, table.get_column(key).dtype).from_database for key, value in attrs.items()}
                new_instance.append(table(**casted_attr))
            response[table] = tuple(new_instance)
            tuple_response.append(tuple(new_instance))
        return tuple(tuple_response)

    def __loop_foo(self) -> dict[Type[Table], list[dict[str, Any]]]:
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
                    agg_methods = self.__get_all_aggregate_method(clause)
                    raise ValueError(f"You cannot use aggregation method like '{agg_methods}' to return model objects. Try specifying 'flavour' attribute as 'dict'.")

                table_attr_dict[table][i][col] = dicc_cols[clause.alias_clause]

        # Convert back to a normal dict if you like (defaultdict is a dict subclass).
        return dict(table_attr_dict)

    def __get_all_aggregate_method(self, clauses: list[ClauseInfo]) -> str:
        """
        Get the class name of those classes that inherit from 'AggregateFunctionBase' class in order to create a better error message.
        """
        res: set[str] = set()
        if not isinstance(clauses, Iterable):
            return clauses.__class__.__name__
        for clause in clauses:
            if isinstance(clause, AggregateFunctionBase):
                res.add(clause.__class__.__name__)
        return ", ".join(res)
