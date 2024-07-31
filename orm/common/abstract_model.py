from typing import Any, Callable, Optional, Type, override, Iterable, Literal
from enum import Enum
from collections import defaultdict
from abc import abstractmethod
import inspect

from orm.utils import ForeignKey, Table

from orm.common.interfaces import IQuery, IStatements, IRepositoryBase
from orm.components.insert import InsertQueryBase
from orm.components.select import ISelect
from orm.components.delete import DeleteQueryBase
from orm.components.upsert import UpsertQueryBase
from orm.components.select import TableColumn
from orm.components.where.abstract_where import AbstractWhere


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


class AbstractSQLStatements[T: Table, TRepo: IRepositoryBase](IStatements[T]):
    __slots__ = ("_model", "_repository", "_query_list")
    __order__: tuple[str, ...] = ("select", "join", "where", "order", "with", "with_recursive", "limit", "offset")

    def __init__(self, model: T, repository: TRepo) -> None:
        self.valid_repository(repository)

        self._model: T = model
        self._repository: TRepo = repository
        self._query_list: dict[ORDER_QUERIES, list[IQuery]] = defaultdict(list)

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica

            raise Exception(f"'{model}' class does not inherit from Table class")

        if model.__table_name__ is Ellipsis:
            raise Exception(f"class variable '__table_name__' must be declared in '{model.__name__}' class")

    @staticmethod
    def valid_repository(repository: Any) -> bool:
        if not isinstance(repository, IRepositoryBase):
            raise ValueError(f"'repository' attribute does not instance of '{IRepositoryBase.__name__}'")
        return True

    @property
    @abstractmethod
    def INSERT_QUERY(self) -> Type[InsertQueryBase[T, TRepo]]: ...

    @property
    @abstractmethod
    def UPSERT_QUERY(self) -> Type[UpsertQueryBase[T]]: ...

    @property
    @abstractmethod
    def DELETE_QUERY(self) -> Type[DeleteQueryBase[T]]: ...
    @property
    @abstractmethod
    def LIMIT_QUERY(self) -> Type[IQuery]: ...
    @property
    @abstractmethod
    def OFFSET_QUERY(self) -> Type[IQuery]: ...
    @property
    @abstractmethod
    def JOIN_QUERY(self) -> Type[IQuery]: ...
    @property
    @abstractmethod
    def WHERE_QUERY(self) -> Type[IQuery]: ...
    @property
    @abstractmethod
    def ORDER_QUERY(self) -> Type[IQuery]: ...
    @property
    @abstractmethod
    def SELECT_QUERY(self) -> ISelect: ...

    @override
    def insert(self, values: T | list[T]) -> None:
        query, values = self.INSERT_QUERY(self._model, self._repository).insert(values)
        self._repository.executemany_with_values(query, values)
        return None

    @override
    def delete(self, instance: Optional[T | list[T]] = None) -> None:
        if instance is None:
            response = self.select()
            if len(response) == 0:
                return None
            # [0] because if we do not select anything, we retrieve all columns of the unic model, stored in tuple[tuple[model]] structure.
            # We always going to have a tuple of one element
            return self.delete(response)

        query, values = self.DELETE_QUERY(self._model).delete(instance)
        self._repository.execute_with_values(query, values)
        return None

    @override
    def upsert(self, values: T | list[T]) -> None:
        query, values = self.UPSERT_QUERY(self._model).upsert(values)
        self._repository.executemany_with_values(query, values)
        return None

    @override
    def limit(self, number: int) -> "IStatements[T]":
        limit = self.LIMIT_QUERY(number)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        limit_list = self._query_list["limit"]
        if len(limit_list) > 0:
            self._query_list["limit"] = [limit]
        else:
            self._query_list["limit"].append(limit)
        return self

    @override
    def offset(self, number: int) -> "IStatements[T]":
        offset = self.OFFSET_QUERY(number)
        self._query_list["offset"].append(offset)
        return self

    @override
    def join(self, table_left: Table, table_right: Table, *, by: str) -> "IStatements[T]":
        where = ForeignKey.MAPPED[table_left.__table_name__][table_right]
        join_query = self.JOIN_QUERY[table_left, Table](table_left, table_right, JoinType(by), where=where)
        self._query_list["join"].append(join_query)
        return self

    @override
    def where(self, lambda_: Callable[[T], bool] = lambda: None, **kwargs) -> "IStatements[T]":
        # FIXME [ ]: I've wrapped self._model into tuple to pass it instance attr. Idk if it's correct
        where_query = self.WHERE_QUERY[T](function=lambda_, instances=(self._model,), **kwargs)
        self._query_list["where"].append(where_query)
        return self

    @override
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderType) -> "IStatements[T]":
        order = self.ORDER_QUERY[T](self._model, _lambda_col, order_type)
        self._query_list["order"].append(order)
        return self

    @override
    def select[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        if len(inspect.signature(selector).parameters) == 0:
            # COMMENT: if we do not specify any lambda function we assumed the user want to retreive only elements of the Model itself avoiding other models
            result = self.select(selector=lambda x: (x,), flavour=flavour, by=by)
            return () if not result else result[0]

        select: ISelect = self.SELECT_QUERY(self._model, select_lambda=selector, by=by)
        self._query_list["select"].append(select)

        query: str = self.build()
        if flavour:
            return self._return_flavour(query, flavour)
        return self._return_model(select, query)

    def _return_flavour[TValue](self, query, flavour: Type[TValue]) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour)

    def _return_model(self, select: ISelect, query: str):
        response_sql = self._repository.read_sql(query, flavour=dict)  # store all columns of the SQL query

        if isinstance(response_sql, Iterable):
            return ClusterQuery(select, response_sql).clean_response()

        return response_sql

    @override
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        self.limit(1)
        if len(inspect.signature(selector).parameters) == 0:
            response = self.select(selector=lambda x: (x,), flavour=flavour, by=by)
        else:
            response = self.select(selector=selector, flavour=flavour, by=by)

        if flavour:
            return response[0]

        # response var could be return more than one element when we work with models an we
        # select columns from different tables using a join query
        if len(response) == 1 and len(response[0]) == 1:
            return response[0][0]
        return tuple([res[0] for res in response])

    @override
    def build(self) -> str:
        query: str = ""

        self._create_necessary_inner_join()
        for x in self.__order__:
            if sub_query := self._query_list.get(x, None):
                if isinstance(sub_query[0], self.WHERE_QUERY):
                    query_ = self.__build_where_clause(sub_query)

                # we must check if any join already exists on query string
                elif isinstance(sub_query[0], self.JOIN_QUERY):
                    select_query: str = self._query_list["select"][0].query
                    query_ = ""
                    for join in sub_query:
                        if join.query not in select_query:
                            query_ += f"\n{join.query}"
                else:
                    query_ = "\n".join([x.query for x in sub_query])

                query += f"\n{query_}" if query != "" else query_
        self._query_list.clear()
        return query

    def __build_where_clause(self, where_condition: list[AbstractWhere]) -> str:
        query: str = where_condition[0].query

        for where in where_condition[1:]:
            q = where.query.replace(where.WHERE, "AND")
            and_, clause = q.split(" ", maxsplit=1)
            query += f" {and_} ({clause})"
        return query

    def _create_necessary_inner_join(self) -> None:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if "where" not in self._query_list:
            return None

        where: AbstractWhere = self._query_list["where"][0]
        involved_tables = where.get_involved_tables()

        select: ISelect = self._query_list["select"][0]
        if not involved_tables or (set(involved_tables) == set(select.tables_heritage)):
            return None

        for l_tbl, r_tbl in involved_tables:
            # FIXME [ ]: Checked what function was called by the self.join method before the change
            self.join(l_tbl, r_tbl, by="INNER JOIN")


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
