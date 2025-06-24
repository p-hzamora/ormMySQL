"""
CLEAN MODERN QUERY BUILDER - NO LEGACY CODE
===========================================

Complete rewrite without any backward compatibility.
Clean, modern implementation using PATH_CONTEXT exclusively.
"""

from __future__ import annotations
from typing import Callable, Optional, Any, TYPE_CHECKING, cast
from abc import ABC, abstractmethod
from ormlambda.sql.clauses import Select, Where, Having, Order, GroupBy, Limit, Offset, JoinSelector

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
    from ormlambda.sql.context import PathContext

from ormlambda import ColumnProxy

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
    )

    def __init__(
        self,
        select: Optional[Select] = None,
        where: Optional[Where] = None,
        having: Optional[Having] = None,
        order: Optional[Order] = None,
        group_by: Optional[GroupBy] = None,
        limit: Optional[Limit] = None,
        offset: Optional[Offset] = None,
        joins: Optional[set[JoinSelector]] = None,
    ):
        self.select = select
        self.where = where
        self.having = having
        self.order = order
        self.group_by = group_by
        self.limit = limit
        self.offset = offset
        self.joins = joins or set()

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
            where_sql = self._compile_where(components.where)
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

        sorted_joins = JoinSelector.sort_join_selectors(joins)
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


class QueryBuilder(IQuery):
    dialect: Dialect
    path_contex: PathContext
    compiler: StandardSQLCompiler
    components: QueryComponents
    join_type: JoinType

    def __init__(self, dialect: Dialect):
        self.dialect = dialect
        self.path_context = self._get_global_context()

        # Strategy pattern for join detection and compilation
        self.compiler = StandardSQLCompiler(dialect)

        # Clean component storage
        self.components = QueryComponents()
        self.join_type = JoinType.INNER_JOIN

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
        return self

    def add_where(self, where: Where) -> QueryBuilder:
        """Add WHERE clause"""
        self.components.where = where
        return self

    def add_having(self, having: Having) -> QueryBuilder:
        """Add HAVING clause"""
        self.components.having = having
        return self

    def add_order(self, order: Order) -> QueryBuilder:
        """Add ORDER BY clause"""
        self.components.order = order
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
        }

        method = clause_selector.get(clause_type,None)
        if not method:
            raise ValueError(f"Unknown clause type: {clause_type}")

        return method(clause)

    # =============================================================================
    # QUERY GENERATION
    # =============================================================================

    def query(self, dialect: Optional[Dialect]=None) -> str:
        target_dialect = dialect or self.dialect

        # Detect required joins

        detected_joins = self.pop_tables_and_create_joins_from_ForeignKey(self.by)
        all_joins = self.components.joins | detected_joins

        # Compile to SQL
        return self.compiler.compile(self.components, all_joins)

    def pop_tables_and_create_joins_from_ForeignKey(self, by: JoinType = JoinType.INNER_JOIN) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.

        joins = set()
        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for column in self.components.select.columns:
            fks = cast(ColumnProxy, column)._path.get_foreign_keys()
            for fk in fks:
                fk_alias = fk.get_alias(self.dialect)
                join = JoinSelector(fk.resolved_function(self.dialect), by, alias=fk_alias, dialect=self.dialect)
                # self._context._add_table_alias(fk.tright, fk_alias)
                # join = JoinSelector(fk.resolved_function(self._context), by, context=self._context, alias=fk_alias, dialect=self.dialect)
                joins.add(join)

        return joins

    def clear(self) -> QueryBuilder:
        """Clear all components"""
        self.components.clear()
        return self

    @property
    def by(self) -> Optional[JoinType]:
        return self.join_type

    @by.setter
    def by(self, value: JoinType) -> None:
        self.join_type = value
