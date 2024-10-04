from __future__ import annotations
from typing import Any, Type, override, Iterable, Literal, TYPE_CHECKING
from collections import defaultdict


from ormlambda.utils import Table
from ormlambda.common.interfaces import IQuery, IRepositoryBase, IStatements_two_generic

if TYPE_CHECKING:
    from ormlambda.components.select import ISelect
    from ormlambda.components.select import TableColumn


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


class AbstractSQLStatements[T: Table, TRepo](IStatements_two_generic[T, TRepo]):
    __slots__ = ("_model", "_repository", "_query_list")
    __order__: tuple[str, ...] = ("select", "join", "where", "order", "with", "group by", "limit", "offset")

    def __init__(self, model: T, repository: IRepositoryBase[TRepo]) -> None:
        self.__valid_repository(repository)

        self._model: T = model
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

    @property
    @override
    def repository(self) -> IRepositoryBase[TRepo]: ...

    def _return_flavour[TValue](self, query, flavour: Type[TValue]) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour)

    def _return_model(self, select: ISelect, query: str):
        response_sql = self._repository.read_sql(query, flavour=dict)  # store all columns of the SQL query

        if isinstance(response_sql, Iterable):
            return ClusterQuery(select, response_sql).clean_response()

        return response_sql


class ClusterQuery:
    def __init__(self, select: ISelect, response_sql: tuple[dict[str, Any]]) -> None:
        self._select: ISelect = select
        self._response_sql: tuple[dict[str, Any]] = response_sql

    def loop_foo(self) -> dict[Type[Table], list[Table]]:
        #  We must ensure to get the valid attributes for each instance
        table_initialize = defaultdict(list)

        unic_table: dict[Table, list[TableColumn]] = defaultdict(list)
        for table_col in self._select.select_list:
            unic_table[table_col._table].append(table_col)

        for table_, table_col in unic_table.items():
            for dicc_cols in self._response_sql:
                valid_attr: dict[str, Any] = {}
                for col in table_col:
                    valid_attr[col.real_column] = dicc_cols[col.alias]
                # COMMENT: At this point we are going to instantiate Table class with specific attributes getting directly from database
                table_initialize[table_].append(table_(**valid_attr))
        return table_initialize

    def clean_response(self) -> tuple[dict[Type[Table], tuple[Table]]]:
        tbl_dicc: dict[Type[Table], list[Table]] = self.loop_foo()

        # it not depend of flavour attr
        for key, val in tbl_dicc.items():
            tbl_dicc[key] = tuple(val)

        return tuple(tbl_dicc.values())
