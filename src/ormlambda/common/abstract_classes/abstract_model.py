from __future__ import annotations
from typing import Any, Type, override, Iterable, Literal, TYPE_CHECKING, Optional
from collections import defaultdict
import abc


from ormlambda.utils import Table
from ormlambda.common.interfaces import IQuery, IRepositoryBase, IStatements_two_generic
from ormlambda.common.interfaces.IAggregate import IAggregate

if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
    from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class AbstractSQLStatements[T: Table, *Ts, TRepo](IStatements_two_generic[T, *Ts, TRepo]):
    __slots__ = ("_model", "_repository", "_query_list")
    __order__: tuple[str, ...] = ("select", "join", "where", "order", "with", "group by", "limit", "offset")

    def __init__(self, model: tuple[T, *Ts], repository: IRepositoryBase[TRepo]) -> None:
        self.__valid_repository(repository)

        self._query: Optional[str] = None
        self._model: T = model[0] if isinstance(model, Iterable) else model
        self._models: tuple[T, *Ts] = self._model if isinstance(model, Iterable) else (model,)
        self._repository: IRepositoryBase[TRepo] = repository
        self._query_list: dict[ORDER_QUERIES, list[IQuery]] = defaultdict(list)

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica
            raise Exception(f"'{model}' class does not inherit from Table class")

    @staticmethod
    def __valid_repository(repository: Any) -> bool:
        if not isinstance(repository, IRepositoryBase):
            raise ValueError(f"'repository' attribute does not instance of '{IRepositoryBase.__name__}'")
        return True

    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    def _return_flavour[TValue](self, query, flavour: Type[TValue], select, **kwargs) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour, model=self._model, select=select, **kwargs)

    def _return_model(self, select, query: str):
        response_sql = self._repository.read_sql(query, flavour=dict, model=self._model, select=select)  # store all columns of the SQL query

        if isinstance(response_sql, Iterable):
            return ClusterQuery[T](select, response_sql).clean_response()

        return response_sql

    @abc.abstractmethod
    def _build(sef): ...

    @property
    def query(self) -> str:
        return self._query

    @property
    def model(self) -> Type[T]:
        return self._model

    @property
    def models(self) -> tuple[*Ts]:
        return self._models

    @property
    @override
    def repository(self) -> IRepositoryBase[TRepo]: ...


class ClusterQuery[T]:
    def __init__(self, select: DecompositionQueryBase[T], response_sql: tuple[dict[str, Any]]) -> None:
        self._select: DecompositionQueryBase[T] = select
        self._response_sql: tuple[dict[str, Any]] = response_sql

    def clean_response(self) -> tuple[dict[Type[Table], tuple[Table]]]:
        tbl_dicc: dict[Type[Table], list[Table]] = self.__loop_foo()

        # it not depend of flavour attr
        for key, val in tbl_dicc.items():
            tbl_dicc[key] = tuple(val)

        return tuple(tbl_dicc.values())

    def __loop_foo(self) -> dict[Type[Table], list[Table]]:
        #  We must ensure to get the valid attributes for each instance
        table_initialize = defaultdict(list)

        for table, clauses in self._select._clauses_group_by_tables.items():
            for dicc_cols in self._response_sql:
                valid_attr: dict[str, Any] = {}
                for clause in clauses:
                    if clause.column is None or not hasattr(table, clause.column):
                        agg_methods = self.__get_all_aggregate_method(clauses)
                        raise ValueError(f"You cannot use aggregation method like '{agg_methods}' to return model objects. Try specifying 'flavour' attribute as 'dict'.")
                    valid_attr[clause.column] = dicc_cols[clause.alias]

                # COMMENT: At this point we are going to instantiate Table class with specific attributes getting directly from database
                table_initialize[table].append(table(**valid_attr))
        return table_initialize

    def __get_all_aggregate_method(self, clauses: list[ClauseInfo]) -> str:
        res: set[str] = set()

        for clause in clauses:
            row = clause._row_column
            if isinstance(row, IAggregate):
                res.add(row.__class__.__name__)
        return ", ".join(res)
