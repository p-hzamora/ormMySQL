from __future__ import annotations
from typing import Callable, Generator, Optional, TYPE_CHECKING, Iterable, overload, Concatenate
from ormlambda.sql.clauses import (
    Select,
    Where,
    Having,
    Order,
    GroupBy,
    Limit,
    Offset,
    JoinSelector,
)

from ormlambda.sql.functions import Count
from ormlambda.sql.comparer import Comparer, ComparerCluster


if TYPE_CHECKING:
    from ormlambda.sql.functions.interface import IFunction
    from ormlambda.dialects import Dialect

from ormlambda import ColumnProxy, TableProxy
import ormlambda.util as util

from ormlambda.common.enums import JoinType, UnionEnum
from ormlambda.sql.elements import ClauseElement
from ormlambda.common.interfaces import IQuery


class StandardSQLCompiler:
    """Standard SQL compiler"""

    def __init__(self, dialect: Dialect):
        self.dialect = dialect

    def compile(self, components: QueryBuilder, joins: set[JoinSelector]) -> str:
        """Compile all components into final SQL"""
        return " ".join(
            (
                components.select.compile(self.dialect).string if components.select else "",
                self._compile_joins(joins),
                components.where.compile(self.dialect).string if components.where else "",
                components.group_by.compile(self.dialect).string if components.group_by else "",
                components.having.compile(self.dialect).string if components.having else "",
                components.order.compile(self.dialect).string if components.order else "",
                components.limit.compile(self.dialect).string if components.limit else "",
                components.offset.compile(self.dialect).string if components.offset else "",
            )
        )

    @util.preload_module("ormlambda.sql.clauses")
    def _compile_joins(self, joins: set[JoinSelector]) -> str:
        """Compile JOIN clauses"""

        if not joins:
            return ""

        JoinSelector = util.preloaded.sql_clauses.JoinSelector

        sorted_joins = JoinSelector.sort_joins_by_alias(joins)
        return " ".join(join.compile(self.dialect).string for join in sorted_joins)


class ColumnIterable[T: TableProxy | ColumnProxy]:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[T], /) -> None: ...

    def __init__(self, iterable=None):
        self.iterable: list = iterable if iterable is not None else []

    def __repr__(self):
        return self.iterable.__repr__()

    def append(self, object: T, /) -> None:
        if isinstance(object, TableProxy):
            self.extend(object.get_columns())
            return None

        return self.iterable.append(object)

    def extend(self, iterable: Iterable[T], /) -> None:
        for item in iterable:
            if isinstance(item, TableProxy):
                self.iterable.extend(item.get_columns())
            else:
                self.iterable.append(item)
        return None

    def clear(self) -> None:
        return self.iterable.clear()

    def __iter__(self) -> Generator[ColumnProxy, None, None]:
        yield from self.iterable

    def __len__(self) -> int:
        return len(self.iterable)

    def __getitem__(self, index: int) -> T:
        return self.iterable[index]


def call_used_column[T, **P](f: Callable[Concatenate[QueryBuilder, IFunction, P], T]) -> Callable[Concatenate[QueryBuilder, IFunction, P], T]:
    def wrapped(self: QueryBuilder, aggregate: IFunction, *args: P.args, **kwargs: P.kwargs):
        self.used_columns.extend(aggregate.used_columns())
        return f(self, aggregate, *args, **kwargs)

    return wrapped


class QueryBuilder(IQuery):
    used_columns: ColumnIterable[ColumnProxy]
    join_type: JoinType

    __slots__ = (
        "select",
        "where",
        "having",
        "order",
        "group_by",
        "limit",
        "offset",
        "joins",
        "count",
        "join_type",
        "used_columns",
    )

    def __init__(self):
        self.__initialize()

    def __initialize(self) -> None:
        """Reset all components"""
        self.select: Optional[Select] = None
        self.where: Optional[Where] = Where()
        self.having: Optional[Having] = Having()
        self.order: Optional[Order] = None
        self.group_by: Optional[GroupBy] = None
        self.limit: Optional[Limit] = None
        self.offset: Optional[Offset] = None
        self.joins: Optional[set[JoinSelector]] = {}
        self.count: Optional[Count] = None

        self.join_type = JoinType.INNER_JOIN
        self.used_columns = ColumnIterable()
        return None

    def clear(self) -> None:
        return self.__initialize()

    @call_used_column
    def add_select(self, select: Select) -> None:
        self.select = select
        return None

    def add_where(self, comparer: list[Comparer | ComparerCluster], union: UnionEnum) -> None:
        for cond in comparer:
            self.used_columns.extend(cond.used_columns())

        self.where.add_comparer_tuple(comparer, union)
        return None

    def add_having(self, comparer: list[Comparer | ComparerCluster], union) -> None:
        for cond in comparer:
            self.used_columns.extend(cond.used_columns())

        self.having.add_comparer_tuple(comparer, union)
        return None

    @call_used_column
    def add_order(self, order: Order) -> None:
        self.order = order
        return None

    @call_used_column
    def add_group_by(self, group_by: GroupBy) -> None:
        self.group_by = group_by
        return None

    def add_limit(self, limit: Limit) -> None:
        self.limit = limit
        return None

    def add_offset(self, offset: Offset) -> None:
        self.offset = offset
        return None

    @call_used_column
    def add_join(self, join: JoinSelector) -> None:
        self.joins.add(join)
        return None

    @call_used_column
    def add_count(self, count: Count) -> None:
        self.count = count
        return None

    def set_join_type(self, join_type: JoinType) -> None:
        self.join_type = join_type
        return None

    def add_statement(self, clause: ClauseElement) -> None:
        """
        Add any clause element - determines type automatically

        This provides a single entry point for all clause types
        while maintaining clean type-specific methods above
        """
        clause_type = type(clause)

        clause_selector: dict[str, Callable[[ClauseElement], QueryBuilder]] = {
            Select: self.add_select,
            Where: self.add_where,
            ComparerCluster: self.add_where,
            Comparer: self.add_where,
            Having: self.add_having,
            Order: self.add_order,
            GroupBy: self.add_group_by,
            Limit: self.add_limit,
            Offset: self.add_offset,
            JoinSelector: self.add_join,
            Count: self.add_count,
        }

        method = clause_selector.get(clause_type, None)
        if not method:
            raise ValueError(f"Unknown clause type: {clause_type}")

        return method(clause)

    def query(self, dialect: Optional[Dialect] = None) -> str:
        all_joins = self.get_joins(dialect)
        return StandardSQLCompiler(dialect).compile(self, all_joins)

    def get_joins(self, dialect) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.

        joins: set[JoinSelector] = set()

        join_type = self.by if self.by != JoinType.INNER_JOIN else JoinType.LEFT_INCLUSIVE
        for column in self.used_columns:
            if not column.number_table_in_chain():
                continue  # It would be the same table so we don't need any join clause

            temp_joins = column.get_relations(join_type, dialect)

            [joins.add(x) for x in temp_joins]

        sorted_joins = JoinSelector.sort_joins_by_alias(joins)
        return sorted_joins

    @property
    def by(self) -> Optional[JoinType]:
        return self.join_type

    @by.setter
    def by(self, value: JoinType) -> None:
        self.join_type = value
