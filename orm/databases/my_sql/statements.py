from collections import defaultdict
import inspect
from typing import Any, Callable, Optional, Type, override, Iterable


from orm.abstract_model import AbstractSQLStatements
from orm.utils import ForeignKey, Table, Column

from orm.interfaces import IStatements, ISelect


from .clauses.joins import JoinSelector, JoinType
from .clauses.select import SelectQuery, TableColumn
from .clauses.limit import LimitQuery
from .clauses.where_condition import WhereCondition
from .clauses.order import OrderQuery, OrderType
from .clauses.offset import OffsetQuery

from orm.interfaces import IRepositoryBase


class MySQLStatements[T: Table](AbstractSQLStatements[T], IStatements[T]):
    def __init__(self, model: T, repository: IRepositoryBase) -> None:
        super().__init__(model, repository=repository)

    # region Private methods
    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    # endregion

    @override
    def insert(self, values: T | list[T]) -> None:
        def __is_valid(column: Column) -> bool:
            """
            Validamos si la columna la debemos eliminar o no a la hora de insertar o actualizar valores.

            Querremos elimina un valor de nuestro objeto cuando especifiquemos un valor que en la bbdd sea AUTO_INCREMENT o AUTO GENERATED ALWAYS AS (__) STORED.

            RETURN
            -----

            - True  -> No eliminamos la columna de la consulta
            - False -> Eliminamos la columna
            """
            cond_1 = all([column.column_value is None, column.is_primary_key])
            cond_2 = any([column.is_auto_increment, column.is_auto_generated])

            # not all to get False and deleted column
            return not all([cond_1, cond_2])

        def __create_dict_list(cls, _list: list, values: T | list[T]):
            if issubclass(values.__class__, Table):
                dicc: dict = {}
                for col in values.__dict__.values():
                    if isinstance(col, Column) and __is_valid(col):
                        dicc.update({col.column_name: col.column_value})
                _list.append(dicc)

            elif isinstance(values, list):
                for x in values:
                    __create_dict_list(_list, x)
            else:
                raise Exception(f"Tipo de dato'{type(values)}' no esperado")

        lista: list = []
        self.__create_dict_list(lista, values)

        self._repository.insert(self._model.__table_name__, lista)
        return None

    @override
    def delete(self, instance: Optional[T | list[T]] = None) -> None:
        if instance is None:
            response = self.select()
            if len(response) == 0:
                return None
            # [0] because if we do not select anything, we retrieve all columns of the unic model, stored in tuple[tuple[model]] structure.
            # We always going to have a tuple of one element
            return self.delete(response[0])

        col: str = ""
        if issubclass(instance.__class__, Table):
            pk = instance.get_pk()
            if pk.column_value is None:
                raise Exception(f"You cannot use 'DELETE' query without set primary key in '{instance.__table_name__}'")
            col = pk.column_name
            value = str(pk.column_value)

        elif isinstance(instance, Iterable):
            value = []
            for ins in instance:
                pk = ins.get_pk()
                col = pk.column_name
                value.append(str(pk.column_value))
        else:
            raise Exception(f"'{type(instance)}' data not expected")

        self._repository.delete(self._model.__table_name__, col=col, value=value)
        return None

    @override
    def upsert(self, values: list[T]) -> None:
        def is_valid(column: Column) -> bool:
            """
            Eliminamos aquellas columnas autogeneradas y dejamos aquellas columnas unicas para que la consulta falle y realice un upsert

            Aunque una pk sea autogenerada debemos eliminarla de la query ya que no podemos pasar un valor a una columna la cual no acepta valores nuevos.
            Cuando se genere dicha columna y la base de datos detecte que el valor generado está repetido, será entonces cuando detecte la duplicidad y realice ON DUPLICATE KEY UPDATE

            RETURN
            -----

            - True  -> No eliminamos la columna de la consulta
            - False -> Eliminamos la columna
            """
            if (column.is_auto_increment and not column.is_primary_key) or column.is_auto_generated:
                return False
            return True

        def create_dict_list(values: T | list[T]):
            """
            Utilizamos lista como nonlocal para poder utilizar esta funcion de forma reciproca
            """
            nonlocal lista

            if issubclass(values.__class__, Table):
                dicc: dict = {}
                for col in values.__dict__.values():
                    if isinstance(col, Column) and is_valid(col):
                        dicc.update({col.column_name: col.column_value})
                lista.append(dicc)

            elif isinstance(values, list):
                for x in values:
                    create_dict_list(x)
            else:
                raise Exception(f"Tipo de dato'{type(values)}' no esperado")

        lista: list = []
        create_dict_list(values)
        self._repository.upsert(self._model.__table_name__, lista)
        return None

    @override
    def limit(self, number: int) -> "IStatements":
        limit: LimitQuery = LimitQuery(number)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        limit_list = self._query_list["limit"]
        if len(limit_list) > 0:
            self._query_list["limit"] = [limit]
        else:
            self._query_list["limit"].append(limit)
        return self

    @override
    def offset(self, number: int) -> "IStatements":
        offset: OffsetQuery = OffsetQuery(number)
        self._query_list["offset"].append(offset)
        return self

    @override
    def join(self, table_left: Table, table_right: Table, *, by: str) -> "IStatements":
        where = ForeignKey.MAPPED[table_left.__table_name__][table_right]
        join_query = JoinSelector[table_left, Table](table_left, table_right, JoinType(by), where=where)
        self._query_list["join"].append(join_query)
        return self

    @override
    def where(self, lambda_: Callable[[T], bool] = lambda: None, **kwargs) -> "IStatements":
        # FIXME [ ]: I've wrapped self._model into tuple to pass it instance attr. Idk if it's correct
        where_query = WhereCondition[T](function=lambda_, instances=(self._model,), **kwargs)
        self._query_list["where"].append(where_query)
        return self

    @override
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderType) -> "IStatements":
        order = OrderQuery[T](self._model, _lambda_col, order_type)
        self._query_list["order"].append(order)
        return self

    @override
    def select[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        select = SelectQuery[T, *Ts](self._model, select_lambda=selector, by=by)
        self._query_list["select"].append(select)

        if len(inspect.signature(selector).parameters) == 0:
            # COMMENT: if we do not specify any lambda function we assumed the user want to retreive only elements of the Model itself avoiding other models
            result = self.select(selector=lambda x: (x,), flavour=flavour, by=by)
            return () if not result else result[0]

        query: str = self.build()
        if flavour:
            return self._return_flavour(query, flavour)
        return self._return_model(select, query)

    def _return_flavour[TValue](self, query, flavour: Type[TValue]) -> tuple[TValue]:
        return self._repository.read_sql(query, flavour=flavour)

    def _return_model[TValue, *Ts](self, select: ISelect, query: str) -> TValue | tuple[tuple[*Ts]]:
        response_sql = self._repository.read_sql(query, flavour=dict)  # store all columns of the SQL query

        if isinstance(response_sql, Iterable):
            return ClusterQuery(select, response_sql).clean_response()

        return response_sql

    @override
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN): ...
    @override
    def build(self) -> str:
        query: str = ""
        self._create_necessary_inner_join()
        for x in self.__order__:
            if sub_query := self._query_list.get(x, None):
                if isinstance(sub_query[0], WhereCondition):
                    query_ = self.__build_where_clause(sub_query)

                # we must check if any join already exists on query string
                elif isinstance(sub_query[0], JoinSelector):
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

    def __build_where_clause(self, where_condition: list[WhereCondition]) -> str:
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
        where: WhereCondition = self._query_list["where"][0]
        involved_tables = where.get_involved_tables()
        if not involved_tables:
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
        for table_col in self._select._select_list:
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
