"""
CLEAN MODERN QUERY BUILDER - NO LEGACY CODE
===========================================

Complete rewrite without any backward compatibility.
Clean, modern implementation using PATH_CONTEXT exclusively.
"""

from __future__ import annotations
from typing import Callable, Generator, Optional, TYPE_CHECKING, Iterable, overload
from abc import ABC, abstractmethod
from ormlambda.sql.clauses import Select, Where, Having, Order, GroupBy, Limit, Offset, JoinSelector
from ormlambda.sql.comparer import Comparer

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
    from ormlambda.sql.context import PathContext
    from ormlambda import Count

from ormlambda import ColumnProxy, TableProxy

from ormlambda.common.enums import JoinType
from ormlambda.sql.elements import ClauseElement
from ormlambda.common.interfaces import IQuery

# =============================================================================
# CLEAN QUERY COMPONENTS
# =============================================================================


class QueryComponents:
    """Clean storage for all query components"""

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
    )

    def __init__(
        self,
    ):
        self.select: Optional[Select] = None
        self.where: Optional[list[Where]] = []
        self.having: Optional[Having] = None
        self.order: Optional[Order] = None
        self.group_by: Optional[GroupBy] = None
        self.limit: Optional[Limit] = None
        self.offset: Optional[Offset] = None
        self.joins: Optional[set[JoinSelector]] = {}
        self.count: Optional[Count] = None

    def clear(self) -> None:
        """Reset all components"""

        for att_name in self.__slots__:
            default = None if att_name != "joins" else set()
            setattr(self, att_name, default)


# =============================================================================
# QUERY COMPILER INTERFACE
# =============================================================================


class IQueryCompiler(ABC):
    """Interface for query compilation strategies"""

    @abstractmethod
    def compile(self, components: QueryComponents, joins: set[JoinSelector]) -> str:
        """Compile query components into SQL string"""
        pass


class StandardSQLCompiler(IQueryCompiler):
    """Standard SQL compiler"""

    def __init__(self, dialect: Dialect):
        self.dialect = dialect

    def compile(self, components: QueryComponents, joins: set[JoinSelector]) -> str:
        """Compile all components into final SQL"""
        query_parts = []

        # SELECT
        if components.select:
            query_parts.append(components.select.compile(self.dialect).string)

        # JOINs
        joins_sql = self._compile_joins(joins)
        if joins_sql:
            query_parts.append(joins_sql)

        # WHERE
        if components.where:
            where_sql = Comparer.join_comparers([x._comparer for x in components.where], dialect= self.dialect)
            if where_sql:
                query_parts.append(where_sql)

        # GROUP BY
        if components.group_by:
            query_parts.append(components.group_by.compile(self.dialect).string)

        # HAVING
        if components.having:
            having_sql = self._compile_having(components.having)
            if having_sql:
                query_parts.append(having_sql)

        # ORDER BY
        if components.order:
            query_parts.append(components.order.compile(self.dialect).string)

        # LIMIT
        if components.limit:
            query_parts.append(components.limit.compile(self.dialect).string)

        # OFFSET
        if components.offset:
            query_parts.append(components.offset.compile(self.dialect).string)

        return " ".join(query_parts)

    def _compile_joins(self, joins: set[JoinSelector]) -> Optional[str]:
        """Compile JOIN clauses"""
        if not joins:
            return None

        from ormlambda.sql.clauses import JoinSelector

        sorted_joins = JoinSelector.sort_joins_by_alias(joins)
        return " ".join(join.query(self.dialect) for join in sorted_joins)

    def _compile_where(self, where: Where) -> Optional[str]:
        """Compile WHERE clause"""

        # Note: No more context parameter needed - PATH_CONTEXT handles it
        return where.compile(self.dialect)

    def _compile_having(self, having: Having) -> Optional[str]:
        """Compile HAVING clause"""

        # Note: No more context parameter needed - PATH_CONTEXT handles it
        return having.compile(self.dialect)

    # =============================================================================
    # MODERN QUERY BUILDER
    # =============================================================================


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


class QueryBuilder(IQuery):
    path_contex: PathContext
    compiler: StandardSQLCompiler
    components: QueryComponents
    used_columns: ColumnIterable[ColumnProxy]
    join_type: JoinType

    def __init__(self):
        self.path_context = self._get_global_context()

        # Clean component storage
        self.components = QueryComponents()
        self.join_type = JoinType.INNER_JOIN
        self.used_columns = ColumnIterable()

    @staticmethod
    def _get_global_context() -> PathContext:
        from ormlambda.sql.context import PATH_CONTEXT

        return PATH_CONTEXT

    # =============================================================================
    # CLEAN CLAUSE MANAGEMENT
    # =============================================================================

    def add_select(self, select: Select) -> QueryBuilder:
        """Add SELECT clause"""
        self.components.select = select
        for col in select.columns:
            if isinstance(col, ColumnProxy):
                self.used_columns.append(col)
            else:
                pass
        return self

    def add_where(self, where: Where) -> QueryBuilder:
        """Add WHERE clause"""
        self.components.where.append(where)
        self.used_columns.extend(where.used_columns())
        return self

    def add_having(self, having: Having) -> QueryBuilder:
        """Add HAVING clause"""
        self.components.having = having
        return self

    def add_order(self, order: Order) -> QueryBuilder:
        """Add ORDER BY clause"""
        self.components.order = order
        self.used_columns.extend(order.used_columns())
        return self

    def add_group_by(self, group_by: GroupBy) -> QueryBuilder:
        """Add GROUP BY clause"""
        self.components.group_by = group_by
        return self

    def add_limit(self, limit: Limit) -> QueryBuilder:
        """Add LIMIT clause"""
        self.components.limit = limit
        return self

    def add_offset(self, offset: Offset) -> QueryBuilder:
        """Add OFFSET clause"""
        self.components.offset = offset
        return self

    def add_join(self, join: JoinSelector) -> QueryBuilder:
        """Add explicit JOIN"""
        self.components.joins.add(join)
        return self

    def add_count(self, count: Count) -> QueryBuilder:
        """Add explicit JOIN"""
        self.components.count = count
        return self

    def set_join_type(self, join_type: JoinType) -> QueryBuilder:
        """set default join type"""
        self.join_type = join_type
        return self

    # =============================================================================
    # GENERIC CLAUSE ADDITION (for existing code compatibility)
    # =============================================================================

    def add_statement(self, clause: ClauseElement) -> QueryBuilder:
        """
        Add any clause element - determines type automatically

        This provides a single entry point for all clause types
        while maintaining clean type-specific methods above
        """
        clause_type = type(clause).__name__

        clause_selector: dict[str, Callable[[ClauseElement], QueryBuilder]] = {
            "Select": self.add_select,
            "Where": self.add_where,
            "Having": self.add_having,
            "Order": self.add_order,
            "GroupBy": self.add_group_by,
            "Limit": self.add_limit,
            "Offset": self.add_offset,
            "JoinSelector": self.add_join,
            "Count": self.add_count,
        }

        method = clause_selector.get(clause_type, None)
        if not method:
            raise ValueError(f"Unknown clause type: {clause_type}")

        return method(clause)

    # =============================================================================
    # QUERY GENERATION
    # =============================================================================

    def query(self, dialect: Optional[Dialect] = None) -> str:
        # Detect required joins
        all_joins = self.pop_tables_and_create_joins_from_ForeignKey(dialect)

        # Compile to SQL
        return StandardSQLCompiler(dialect).compile(self.components, all_joins)

    def pop_tables_and_create_joins_from_ForeignKey(self, dialect) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.

        joins: set[JoinSelector] = set()

        join_type = self.by if self.by != JoinType.INNER_JOIN else JoinType.LEFT_INCLUSIVE
        for column in self.used_columns:
            if not column.number_table_in_chain():  # It would be the same table
                continue
            temp_joins = column.get_relations(join_type, dialect)

            [joins.add(x) for x in temp_joins]

        sorted_joins = JoinSelector.sort_joins_by_alias(joins)
        return sorted_joins

    def clear(self) -> QueryBuilder:
        """Clear all components"""
        self.components.clear()
        self.used_columns.clear()
        return self

    @property
    def by(self) -> Optional[JoinType]:
        return self.join_type

    @by.setter
    def by(self, value: JoinType) -> None:
        self.join_type = value
