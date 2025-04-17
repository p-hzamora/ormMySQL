from __future__ import annotations
from typing import Concatenate, Iterable, TypedDict, override, Type, TYPE_CHECKING, Any, Callable, Optional
from mysql.connector import errors, errorcode

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql.clauses.joins import JoinSelector
from ormlambda import ForeignKey

from ormlambda.common.interfaces import IQuery
from mysql.connector import MySQLConnection


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.statements.types import OrderTypes
    from ormlambda.sql.types import ColumnType
    from ormlambda.statements.types import SelectCols
    from ormlambda.repository.interfaces import IRepositoryBase
    from ormlambda.statements.interfaces import IStatements_two_generic
    from ormlambda.repository.interfaces.IRepositoryBase import TypeExists
    from ormlambda.sql.clause_info import IAggregate
    from ormlambda.statements.types import WhereTypes


from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.statements import BaseStatement
from .clauses import DeleteQuery
from .clauses import InsertQuery
from .clauses import Limit
from .clauses import Offset
from .clauses import Order
from .clauses import Select

from .clauses import UpsertQuery
from .clauses import UpdateQuery
from .clauses import Where
from .clauses import Having
from .clauses import Count
from .clauses import GroupBy
from .clauses import Alias


from ormlambda import Table, Column
from ormlambda.common.enums import JoinType
from . import functions as func
from .join_context import JoinContext, TupleJoinType
from ormlambda.common.global_checker import GlobalChecker


# COMMENT: It's so important to prevent information generated by other tests from being retained in the class.
@staticmethod
def clear_list[T, **P](f: Callable[Concatenate[MySQLStatements, P], T]) -> Callable[P, T]:
    def wrapper(self: MySQLStatements, *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(self, *args, **kwargs)
        except Exception as err:
            raise err
        finally:
            ForeignKey.stored_calls.clear()
            self._query_builder.clear()

    return wrapper


class OrderType(TypedDict):
    Select: Select
    JoinSelector: JoinSelector
    Where: Where
    Order: Order
    GroupBy: GroupBy
    Having: Having
    Limit: Limit
    Offset: Offset


class QueryBuilder(IQuery):
    __order__: tuple[str, ...] = ("Select", "JoinSelector", "Where", "GroupBy", "Having", "Order", "Limit", "Offset")

    def __init__(self, by: JoinType = JoinType.INNER_JOIN):
        self._context = ClauseInfoContext()
        self._query_list: OrderType = {}
        self._by = by

        self._joins: Optional[IQuery] = None
        self._select: Optional[IQuery] = None
        self._where: Optional[IQuery] = None
        self._order: Optional[IQuery] = None
        self._group_by: Optional[IQuery] = None
        self._limit: Optional[IQuery] = None
        self._offset: Optional[IQuery] = None

    def add_statement[T](self, clause: ClauseInfo[T]):
        self.update_context(clause)
        self._query_list[type(clause).__name__] = clause

    @property
    def by(self) -> JoinType:
        return self._by

    @by.setter
    def by(self, value: JoinType) -> None:
        self._by = value

    @property
    def JOINS(self) -> Optional[set[JoinSelector]]:
        return self._joins

    @property
    def SELECT(self) -> IQuery:
        return self._query_list.get("Select", None)

    @property
    def WHERE(self) -> IQuery:
        where = self._query_list.get("Where", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def ORDER(self) -> IQuery:
        return self._query_list.get("Order", None)

    @property
    def GROUP_BY(self) -> IQuery:
        return self._query_list.get("GroupBy", None)

    @property
    def HAVING(self) -> IQuery:
        where = self._query_list.get("Having", None)
        if not isinstance(where, Iterable):
            if not where:
                return ()
            return (where,)
        return where

    @property
    def LIMIT(self) -> IQuery:
        return self._query_list.get("Limit", None)

    @property
    def OFFSET(self) -> IQuery:
        return self._query_list.get("Offset", None)

    @property
    def query(self) -> str:
        # COMMENT: (select.query, query)We must first create an alias for 'FROM' and then define all the remaining clauses.
        # This order is mandatory because it adds the clause name to the context when accessing the .query property of 'FROM'

        extract_joins = self.pop_tables_and_create_joins_from_ForeignKey(self._by)

        JOINS = self.stringify_foreign_key(extract_joins, " ")
        query_list: tuple[str, ...] = (
            self.SELECT.query,
            JOINS,
            Where.join_condition(self.WHERE, True, self._context) if self.WHERE else None,
            self.GROUP_BY.query if self.GROUP_BY else None,
            Having.join_condition(self.HAVING, True, self._context) if self.HAVING else None,
            self.ORDER.query if self.ORDER else None,
            self.LIMIT.query if self.LIMIT else None,
            self.OFFSET.query if self.OFFSET else None,
        )
        return " ".join([x for x in query_list if x])

    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> Optional[str]:
        if not joins:
            return None
        sorted_joins = JoinSelector.sort_join_selectors(joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def pop_tables_and_create_joins_from_ForeignKey(self, by: JoinType = JoinType.INNER_JOIN) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        joins = set()
        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for fk in ForeignKey.stored_calls.copy():
            fk = ForeignKey.stored_calls.pop(fk)
            self._context._add_table_alias(fk.tright, fk.alias)
            join = JoinSelector(fk.resolved_function(self._context), by, context=self._context, alias=fk.alias)
            joins.add(join)

        return joins

    def clear(self) -> None:
        self.__init__()
        return None

    def update_context(self, clause: ClauseInfo) -> None:
        if not hasattr(clause, "context"):
            return None

        if clause.context is not None:
            self._context.update(clause.context)
        clause.context = self._context


class MySQLStatements[T: Table, *Ts](BaseStatement[T, MySQLConnection]):
    def __init__(self, model: tuple[T, *Ts], repository: IRepositoryBase) -> None:
        super().__init__(model, repository=repository)
        self._query_builder = QueryBuilder()

    @property
    @override
    def repository(self) -> IRepositoryBase:
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
        # not necessary to call self._query_builder.clear() because select() method already call it
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
        update = UpdateQuery(self._model, self._repository, self._query_builder.WHERE)
        update.update(dicc)
        update.execute()

        return None

    @override
    def limit(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        limit = Limit(number)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        self._query_builder.add_statement(limit)
        return self

    @override
    def offset(self, number: int) -> IStatements_two_generic[T, MySQLConnection]:
        offset = Offset(number)
        self._query_builder.add_statement(offset)
        return self

    @override
    def count[TProp](
        self,
        selection: None | SelectCols[T,TProp] = lambda x: "*",
        alias="count",
        execute: bool = False,
    ) -> Optional[int]:
        if execute is True:
            return self.select_one(self.count(selection, alias, False), flavour=dict)[alias]

        selection = GlobalChecker.resolved_callback_object(selection, self.models)
        return Count(element=selection, alias_clause=alias, context=self._query_builder._context)

    @override
    def where(self, conditions: WhereTypes) -> IStatements_two_generic[T, MySQLConnection]:
        # FIXME [x]: I've wrapped self._model into tuple to pass it instance attr. Idk if it's correct

        conditions = GlobalChecker.resolved_callback_object(conditions, self._models)
        if not isinstance(conditions, Iterable):
            conditions = (conditions,)
        self._query_builder.add_statement(Where(*conditions))
        return self

    @override
    def having(self, conditions: WhereTypes) -> IStatements_two_generic[T, MySQLConnection]:
        conditions = GlobalChecker.resolved_callback_object(conditions, self._models)
        if not isinstance(conditions, Iterable):
            conditions = (conditions,)
        self._query_builder.add_statement(Having(*conditions))
        return self

    @override
    def order[TValue](self, columns: Callable[[T], TValue], order_type: OrderTypes) -> IStatements_two_generic[T, MySQLConnection]:
        query = GlobalChecker.resolved_callback_object(columns, self._models)
        order = Order(query, order_type)
        self._query_builder.add_statement(order)
        return self

    @override
    def concat(self, selector: SelectCols[T, str], alias: str = "concat") -> IAggregate:
        return func.Concat[T](
            values=selector,
            alias_clause=alias,
            context=self._query_builder._context,
        )

    @override
    def max[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: str = "max",
        execute: bool = False,
    ) -> int:
        column = GlobalChecker.resolved_callback_object(column, self.models)
        if execute is True:
            return self.select_one(self.max(column, alias, execute=False), flavour=dict)[alias]
        return func.Max(elements=column, alias_clause=alias, context=self._query_builder._context)

    @override
    def min[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: str = "min",
        execute: bool = False,
    ) -> int:
        column = GlobalChecker.resolved_callback_object(column, self.models)
        if execute is True:
            return self.select_one(self.min(column, alias, execute=False), flavour=dict)[alias]
        return func.Min(elements=column, alias_clause=alias, context=self._query_builder._context)

    @override
    def sum[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: str = "sum",
        execute: bool = False,
    ) -> int:
        column = GlobalChecker.resolved_callback_object(column, self.models)
        if execute is True:
            return self.select_one(self.sum(column, alias, execute=False), flavour=dict)[alias]
        return func.Sum(elements=column, alias_clause=alias, context=self._query_builder._context)

    @override
    def join[LTable: Table, LProp, RTable: Table, RProp](self, joins: tuple[TupleJoinType[LTable, LProp, RTable, RProp]]) -> JoinContext[tuple[*TupleJoinType[LTable, LProp, RTable, RProp]]]:
        return JoinContext(self, joins, self._query_builder._context)

    @override
    @clear_list
    def select[TValue, TFlavour, *Ts](
        self,
        selector: Optional[tuple[TValue, *Ts]] = None,
        *,
        flavour: Optional[Type[TFlavour]] = None,
        by: JoinType = JoinType.INNER_JOIN,
        **kwargs,
    ):
        select_clause = GlobalChecker.resolved_callback_object(selector, self._models)

        if selector is None:
            # COMMENT: if we do not specify any lambda function we assumed the user want to retreive only elements of the Model itself avoiding other models
            result = self.select(selector=lambda x: x, flavour=flavour, by=by)
            # COMMENT: Always we want to retrieve tuple[tuple[Any]]. That's the reason to return result[0] when we ensure the user want only objects of the first table.
            # Otherwise, we wil return the result itself
            if flavour:
                return result
            return () if not result else result[0]

        select = Select[T, *Ts](
            self._models,
            columns=select_clause,
        )
        self._query_builder.add_statement(select)

        self._query_builder.by = by
        self._query: str = self._query_builder.query

        if flavour:
            result = self._return_flavour(self.query, flavour, select, **kwargs)
            if issubclass(flavour, tuple) and isinstance(select_clause, Column | ClauseInfo):
                return tuple([x[0] for x in result])
            return result
        return self._return_model(select, self.query)

    @override
    def select_one[TValue, TFlavour, *Ts](
        self,
        selector: Optional[tuple[TValue, *Ts]] = None,
        *,
        flavour: Optional[Type[TFlavour]] = None,
        by: JoinType = JoinType.INNER_JOIN,
        **kwargs,
    ):
        self.limit(1)

        response = self.select(selector=selector, flavour=flavour, by=by, **kwargs)

        if not isinstance(response, Iterable):
            return response
        if flavour:
            return response[0] if response else None

        # response var could be return more than one element when we work with models an we
        # select columns from different tables using a join query
        # FIXME [x]: before it was if len(response) == 1 and len(response[0]) == 1: return response[0][0]
        if len(response) == 1:
            if isinstance(response[0], Iterable) and len(response[0]) == 1:
                return response[0][0]
            else:
                return response[0]
        return tuple([res[0] for res in response])

    @override
    def first[TValue, TFlavour, *Ts](
        self,
        selector: Optional[tuple[TValue, *Ts]] = None,
        *,
        flavour: Optional[Type[TFlavour]] = None,
        by: JoinType = JoinType.INNER_JOIN,
        **kwargs,
    ):
        return self.select_one(
            selector=selector,
            flavour=flavour,
            by=by,
            **kwargs,
        )

    @override
    def groupby[TProp](self, column: ColumnType[TProp] | Callable[[T, *Ts], Any]):
        groupby = GroupBy(column=column, context=self._query_builder._context)
        # Only can be one LIMIT SQL parameter. We only use the last LimitQuery
        self._query_builder.add_statement(groupby)
        return self

    @override
    def alias[TProp](self, column: ColumnType[TProp], alias: str) -> ClauseInfo[T, TProp]:
        return Alias(
            table=column.table,
            column=column,
            alias_clause=alias,
            context=self._query_builder._context,
        )
