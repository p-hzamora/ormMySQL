from __future__ import annotations
from typing import Iterable, override, Type, TYPE_CHECKING, Any, Callable, Optional
import inspect
from mysql.connector import MySQLConnection, errors, errorcode


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.components.where.abstract_where import AbstractWhere
    from ormlambda.common.interfaces.IStatements import OrderType
    from ormlambda.common.interfaces import IQuery, IRepositoryBase, IStatements_two_generic
    from ormlambda.common.interfaces.IRepositoryBase import TypeExists
    from ormlambda.common.interfaces import IAggregate
    from ormlambda.common.interfaces.IStatements import WhereTypes

from ormlambda import AbstractSQLStatements
from .clauses import DeleteQuery
from .clauses import InsertQuery
from .clauses import JoinSelector
from .clauses import LimitQuery
from .clauses import OffsetQuery
from .clauses import OrderQuery
from .clauses.select import Select

from .clauses import UpsertQuery
from .clauses import UpdateQuery
from .clauses import WhereCondition
from .clauses import Count
from .clauses import GroupBy


from ormlambda.utils import ForeignKey, Table
from ormlambda.common.enums import JoinType
from . import functions as func


class MySQLStatements[T: Table](AbstractSQLStatements[T, MySQLConnection]):
    def __init__(self, model: T, repository: IRepositoryBase[MySQLConnection]) -> None:
        super().__init__(model, repository=repository)

    @property
    @override
    def repository(self) -> IRepositoryBase[MySQLConnection]:
        return self._repository

    @override
    def create_table(self, if_exists: TypeExists = "fail") -> None:
        name: str = self._model.__table_name__
        if self._repository.table_exists(name):
            if if_exists == "replace":
                self._repository.drop_table(name)

            elif if_exists == "fail":
                raise errors.ProgrammingError(msg=f"Table '{self._model.__table_name__}' already exists", errno=errorcode.ER_TABLE_EXISTS_ERROR)

            elif if_exists == "append":
                counter: int = 0
                char: str = ""
                while self._repository.table_exists(name + char):
                    counter += 1
                    char = f"_{counter}"
                name += char
                self._model.__table_name__ = name

        query = self._model.create_table_query()
        self._repository.execute(query)
        return None

    @override
    def table_exists(self) -> bool:
        return self._repository.table_exists(self._model.__table_name__)

    @override
    def insert(self, instances: T | list[T]) -> None:
        insert = InsertQuery(self._model, self._repository)
        insert.insert(instances)
        insert.execute()
        self._query_list.clear()
        return None

    @override
    def delete(self, instances: Optional[T | list[T]] = None) -> None:
        if instances is None:
            response = self.select()
            if len(response) == 0:
                return None
            # [0] because if we do not select anything, we retrieve all columns of the unic model, stored in tuple[tuple[model]] structure.
            # We always going to have a tuple of one element
            return self.delete(response)

        delete = DeleteQuery(self._model, self._repository)
        delete.delete(instances)
        delete.execute()
        # not necessary to call self._query_list.clear() because select() method already call it
        return None

    @override
    def upsert(self, instances: T | list[T]) -> None:
        upsert = UpsertQuery(self._model, self._repository)
        upsert.upsert(instances)
        upsert.execute()
        self._query_list.clear()
        return None

    @override
    def update(self, dicc: dict[str, Any] | list[dict[str, Any]]) -> None:
        update = UpdateQuery(self._model, self._repository, self._query_list["where"])
        update.update(dicc)
        update.execute()
        self._query_list.clear()
        return None

    @override
    def limit(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        limit = LimitQuery(number)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        limit_list = self._query_list["limit"]
        if len(limit_list) > 0:
            self._query_list["limit"] = [limit]
        else:
            self._query_list["limit"].append(limit)
        return self

    @override
    def offset(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        offset = OffsetQuery(number)
        self._query_list["offset"].append(offset)
        return self

    @override
    def count(
        self,
        selection: Callable[[T], tuple] = lambda x: "*",
        alias=True,
        alias_name=None,
    ) -> IQuery:
        return Count[T](self._model, selection, alias=alias, alias_name=alias_name)

    @override
    def join(self, table_left: Table, table_right: Table, *, by: str) -> IStatements_two_generic[T, MySQLConnection]:
        where = ForeignKey.MAPPED[table_left.__table_name__][table_right.__table_name__]
        join_query = JoinSelector[table_left, Table](table_left, table_right, JoinType(by), where=where)
        self._query_list["join"].append(join_query)
        return self

    @override
    def where(self, conditions: WhereTypes = lambda: None, **kwargs) -> IStatements_two_generic[T, MySQLConnection]:
        # FIXME [x]: I've wrapped self._model into tuple to pass it instance attr. Idk if it's correct

        if isinstance(conditions, Iterable):
            for x in conditions:
                self._query_list["where"].append(WhereCondition[T](function=x, instances=(self._model,), **kwargs))
            return self

        where_query = WhereCondition[T](function=conditions, instances=(self._model,), **kwargs)
        self._query_list["where"].append(where_query)
        return self

    @override
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderType) -> IStatements_two_generic[T, MySQLConnection]:
        order = OrderQuery[T](self._model, _lambda_col, order_type)
        self._query_list["order"].append(order)
        return self

    @override
    def concat[*Ts](self, selector: Callable[[T], tuple[*Ts]], alias: bool = True, alias_name: str = "CONCAT") -> IAggregate[T]:
        return func.Concat[T](self._model, selector, alias=alias, alias_name=alias_name)

    @override
    def max[TProp](self, column: Callable[[T], TProp], alias: bool = True, alias_name: str = "max") -> TProp:
        return func.Max[T](self._model, column=column, alias=alias, alias_name=alias_name)

    @override
    def min[TProp](self, column: Callable[[T], TProp], alias: bool = True, alias_name: str = "min") -> TProp:
        return func.Min[T](self._model, column=column, alias=alias, alias_name=alias_name)

    @override
    def sum[TProp](self, column: Callable[[T], TProp], alias: bool = True, alias_name: str = "sum") -> TProp:
        return func.Sum[T](self._model, column=column, alias=alias, alias_name=alias_name)

    @override
    def select[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        if len(inspect.signature(selector).parameters) == 0:
            # COMMENT: if we do not specify any lambda function we assumed the user want to retreive only elements of the Model itself avoiding other models
            result = self.select(selector=lambda x: (x,), flavour=flavour, by=by)
            # COMMENT: Always we want to retrieve tuple[tuple[Any]]. That's the reason to return result[0] when we ensure the user want only objects of the first table.
            # Otherwise, we wil return the result itself
            if flavour:
                return result
            return () if not result else result[0]
        select = Select[T](self._model, lambda_query=selector, by=by, alias=False)
        self._query_list["select"].append(select)

        query: str = self._build()
        if flavour:
            result = self._return_flavour(query, flavour)
            if issubclass(flavour, tuple) and isinstance(selector(self._model), property):
                return tuple([x[0] for x in result])
            return result
        return self._return_model(select, query)

    @override
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        self.limit(1)
        if len(inspect.signature(selector).parameters) == 0:
            response = self.select(selector=lambda x: (x,), flavour=flavour, by=by)
        else:
            response = self.select(selector=selector, flavour=flavour, by=by)

        if flavour:
            return response[0] if response else None

        # response var could be return more than one element when we work with models an we
        # select columns from different tables using a join query
        if len(response) == 1 and len(response[0]) == 1:
            return response[0][0]
        return tuple([res[0] for res in response])

    @override
    def group_by[*Ts](self, column: str | Callable[[T], Any]) -> IStatements_two_generic[T, MySQLConnection]:
        if isinstance(column, str):
            groupby = GroupBy[T, tuple[*Ts]](self._model, lambda x: column)
        else:
            groupby = GroupBy[T, tuple[*Ts]](self._model, column)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        self._query_list["group by"].append(groupby)
        return self

    @override
    def _build(self) -> str:
        query: str = ""

        for x in self.__order__:
            sub_query: Optional[list[IQuery]] = self._query_list.get(x, None)
            if sub_query is None:
                continue

            if isinstance(sub_query[0], WhereCondition):
                query_ = self.__build_where_clause(sub_query)

            # we must check if any join already exists on query string
            elif isinstance(sub_query[0], JoinSelector):
                select_query: str = self._query_list["select"][0].query
                query_ = ""
                for join in sub_query:
                    if join.query not in select_query:
                        query_ += f"\n{join.query}"

            elif isinstance((select := sub_query[0]), Select):
                query_: str = ""
                where_joins = self.__create_necessary_inner_join()
                if where_joins:
                    select._fk_relationship.update(where_joins)
                query_ = select.query

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

    def __create_necessary_inner_join(self) -> Optional[set[tuple[Type[Table], Type[Table]]]]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if "where" not in self._query_list:
            return None

        res = []
        for where in self._query_list["where"]:
            where: AbstractWhere

            tables = where.get_involved_tables()

            if tables:
                [res.append(x) for x in tables]

        return set(res)
