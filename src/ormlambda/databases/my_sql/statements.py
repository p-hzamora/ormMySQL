from __future__ import annotations
from typing import Iterable, override, Type, TYPE_CHECKING, Any, Callable, Optional
from mysql.connector import MySQLConnection, errors, errorcode
import functools


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.interfaces.IStatements import OrderTypes
    from ormlambda.common.interfaces import IQuery, IRepositoryBase, IStatements_two_generic
    from ormlambda.common.interfaces.IRepositoryBase import TypeExists
    from ormlambda.common.interfaces import IAggregate
    from ormlambda.common.interfaces.IStatements import WhereTypes

from ormlambda.utils.foreign_key import ForeignKey
from ormlambda import AbstractSQLStatements
from .clauses import DeleteQuery
from .clauses import InsertQuery
from .clauses import JoinSelector
from .clauses import LimitQuery
from .clauses import OffsetQuery
from .clauses import Order
from .clauses.select import Select

from .clauses import UpsertQuery
from .clauses import UpdateQuery
from .clauses import Where
from .clauses import Count
from .clauses import GroupBy
from .clauses import Alias


from ormlambda.utils import Table, Column
from ormlambda.common.enums import JoinType
from . import functions as func
from .join_context import JoinContext, TupleJoinType
from ormlambda.utils.global_checker import GlobalChecker


# COMMENT: It's so important to prevent information generated by other tests from being retained in the class.
def clear_list(f: Callable[..., Any]):
    @functools.wraps(f)
    def wrapper(self: MySQLStatements, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        finally:
            self._query_list.clear()

    return wrapper


class MySQLStatements[T: Table, *Ts](AbstractSQLStatements[T, *Ts, MySQLConnection]):
    def __init__(self, model: tuple[T, *Ts], repository: IRepositoryBase[MySQLConnection]) -> None:
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
    @clear_list
    def insert(self, instances: T | list[T]) -> None:
        insert = InsertQuery(self._model, self._repository)
        insert.insert(instances)
        insert.execute()
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
    @clear_list
    def upsert(self, instances: T | list[T]) -> None:
        upsert = UpsertQuery(self._model, self._repository)
        upsert.upsert(instances)
        upsert.execute()
        return None

    @override
    @clear_list
    def update(self, dicc: dict[str, Any] | list[dict[str, Any]]) -> None:
        update = UpdateQuery(self._model, self._repository, self._query_list["where"])
        update.update(dicc)
        update.execute()

        return None

    @override
    def limit(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        limit = LimitQuery(number)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        self._query_list["limit"] = [limit]
        return self

    @override
    def offset(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        offset = OffsetQuery(number)
        self._query_list["offset"] = [offset]
        return self

    @override
    def count(
        self,
        selection: Callable[[T], tuple] = lambda x: "*",
        alias=True,
        alias_name="count",
    ) -> IQuery:
        return Count[T](self._model, selection, alias=alias, alias_name=alias_name)

    @override
    def where(self, conditions: WhereTypes) -> IStatements_two_generic[T, MySQLConnection]:
        # FIXME [x]: I've wrapped self._model into tuple to pass it instance attr. Idk if it's correct

        if GlobalChecker.is_lambda_function(conditions):
            conditions = conditions(self._model)
        if not isinstance(conditions, Iterable):
            conditions = (conditions,)
        self._query_list["where"].append(Where(*conditions))
        return self

    @override
    def order[TValue](self, columns: Callable[[T], TValue], order_type: OrderTypes) -> IStatements_two_generic[T, MySQLConnection]:
        query = columns(self._model) if GlobalChecker.is_lambda_function(columns) else columns
        order = Order(query, order_type)
        self._query_list["order"].append(order)
        return self

    @override
    def concat[*Ts](self, selector: Callable[[T], tuple[*Ts]], alias: bool = True, alias_name: str = "CONCAT") -> IAggregate:
        return func.Concat[T](self._model, selector, alias=alias, alias_name=alias_name, context=self._context)

    @override
    def max[TProp](self, column: Callable[[T], TProp], alias_name: str = "max") -> TProp:
        return func.Max(column=column, alias_clause=alias_name, context=self._context)

    @override
    def min[TProp](self, column: Callable[[T], TProp], alias_name: str = "min") -> TProp:
        return func.Min(column=column, alias_clause=alias_name, context=self._context)

    @override
    def sum[TProp](self, column: Callable[[T], TProp], alias_name: str = "sum") -> TProp:
        return func.Sum(column=column, alias_clause=alias_name, context=self._context)

    # @override
    # def min[TProp](self, column: Callable[[T], TProp], alias: bool = True, alias_name: str = "min") -> TProp:
    #     return func.Min[T](self._model, column=column, alias=alias, alias_name=alias_name)

    # @override
    # def sum[TProp](self, column: Callable[[T], TProp], alias: bool = True, alias_name: str = "sum") -> TProp:
    #     return func.Sum[T](self._model, column=column, alias=alias, alias_name=alias_name)

    @override
    def join[*FKTable](self, joins: tuple[*TupleJoinType[FKTable]]) -> JoinContext[tuple[*TupleJoinType[FKTable]]]:
        for alias, comparer, by in joins:
            self._query_list["join"].append(JoinSelector(comparer, by, alias))
        return JoinContext[T, *FKTable, MySQLConnection](self, joins, self._context)

    # @override
    # def join[*FKTables](
    #     self,
    #     table: Optional[T] = None,
    #     relation: Optional[WhereCondition[T, *FKTables]] = None,
    #     join_type: Optional[JoinType] = None,
    # ) -> IStatements_two_generic[T, *FKTables, MySQLConnection]:
    #     if isinstance(table, type) and issubclass(table, Table):
    #         joins = ((table, relation, join_type),)
    #     else:
    #         if any(len(x) != 3 for x in table):
    #             raise ValueError("Each tuple inside of 'join' method must contain the referenced table, relation between columns and join type")
    #         joins = table

    #     new_tables: list[Type[Table]] = [self._model]

    #     for table, where, by in joins:
    #         new_tables.append(table)
    #         join_query = JoinSelector[T, type(table)](self._model, table, by=by, where=where)
    #         self._query_list["join"].append(join_query)
    #     self._models = new_tables
    #     return self

    @override
    def select[TValue, TFlavour, *Ts](self, selector: Optional[tuple[TValue, *Ts]] = None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN, **kwargs):
        select_clause = selector(self._model) if GlobalChecker.is_lambda_function(selector) else selector

        if selector is None:
            # COMMENT: if we do not specify any lambda function we assumed the user want to retreive only elements of the Model itself avoiding other models
            result = self.select(selector=lambda x: x, flavour=flavour, by=by)
            # COMMENT: Always we want to retrieve tuple[tuple[Any]]. That's the reason to return result[0] when we ensure the user want only objects of the first table.
            # Otherwise, we wil return the result itself
            if flavour:
                return result
            return () if not result else result[0]

        joins = self._query_list.pop("join", None)
        select = Select[T, *Ts](
            self._models,
            lambda_query=select_clause,
            by=by,
            joins=joins,
            context=self._context,
        )
        self._query_list["select"].append(select)

        self._query: str = self._build(by)

        if flavour:
            result = self._return_flavour(self.query, flavour, select, **kwargs)
            if issubclass(flavour, tuple) and isinstance(select_clause, Column):
                return tuple([x[0] for x in result])
            return result
        return self._return_model(select, self.query)

    @override
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[tuple[TValue, *Ts]] = None, *, flavour: Optional[Type[TFlavour]] = None, by: JoinType = JoinType.INNER_JOIN):
        self.limit(1)

        response = self.select(selector=selector, flavour=flavour, by=by)

        if flavour:
            return response[0] if response else None

        # response var could be return more than one element when we work with models an we
        # select columns from different tables using a join query
        # FIXME [ ]: before it was if len(response) == 1 and len(response[0]) == 1: return response[0][0]
        if len(response) == 1:
            return response[0]
        return tuple([res[0] for res in response])

    @override
    def group_by(self, column: str | Callable[[T, *Ts], Any]):
        if isinstance(column, str):
            groupby = GroupBy[T, tuple[*Ts]](self._models, lambda x: column)
        else:
            groupby = GroupBy[T, tuple[*Ts]](self._models, column)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        self._query_list["group by"].append(groupby)
        return self

    @override
    def alias(self, column: Callable[[T, *Ts], Any], alias: str) -> IStatements_two_generic[T, *Ts, MySQLConnection]:
        return Alias[T, *Ts](self.models, column, alias_name=alias)

    @override
    @clear_list
    def _build(self, by: JoinType = JoinType.INNER_JOIN) -> str:
        query_list: list[str] = []
        for x in self.__order__:
            if len(self._query_list) == 0:
                break

            sub_query: Optional[list[IQuery]] = self._query_list.pop(x, None)
            if sub_query is None:
                continue

            if isinstance(sub_query[0], Where):
                query_ = self.__build_where_clause(sub_query)

            elif isinstance((select := sub_query[0]), Select):
                query_: str = ""
                where_joins = self.__create_necessary_inner_join(by)
                if where_joins:
                    select._joins.update(where_joins)
                query_ = select.query

            else:
                query_ = "\n".join([x.query for x in sub_query])

            query_list.append(query_)
        return "\n".join(query_list)

    def __build_where_clause(self, where_condition: list[Where]) -> str:
        if not where_condition:
            return ""
        return Where.join_condition(where_condition, restrictive=True)

    def __create_necessary_inner_join(self, by: JoinType) -> Optional[set[JoinSelector]]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        joins = set()
        for _ in range(len(ForeignKey.stored_calls)):
            fk = ForeignKey.stored_calls.pop()
            joins.add(JoinSelector(fk.resolved_function(), by, context=self._context, alias=fk.alias))
        return joins
