from __future__ import annotations
from collections import defaultdict
from typing import override, Optional, TYPE_CHECKING, Type


from ormlambda.util.module_tree.dfs_traversal import DFSTraversal
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import JoinType
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.sql.comparer import Comparer
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.sql.elements import ClauseElement


# TODOL [x]: Try to import Table module without circular import Error
if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.dialects import Dialect


class JoinSelector[TLeft: Table, TRight: Table](IJoinSelector[TLeft, TRight], ClauseElement):
    __visit_name__ = "join"
    __slots__: tuple = (
        "_comparer",
        "_orig_table",
        "_right_table",
        "_by",
        "_left_col",
        "_right_col",
        "_compareop",
        "_alias",
    )

    @override
    def __repr__(self) -> str:
        table_col_left: str = f"{self.left_table.table_alias()}.{self._left_col}"
        table_col_right: str = f"{self.right_table.table_alias()}.{self._right_col}"

        return f"{IQuery.__name__}: {self.__class__.__name__} ({table_col_left} == {table_col_right})"

    def __init__[LProp, RProp](
        self,
        where: Comparer,
        by: JoinType,
        alias: Optional[str] = "{table}",
        context: ClauseContextType = None,
        *,
        dialect: Dialect,
        **kw,
    ) -> None:
        lcon = where.left_condition(dialect)
        rcon = where.right_condition(dialect)
        self._comparer: Comparer = where
        self._orig_table: TLeft = lcon.table
        self._right_table: TRight = rcon.table
        self._by: JoinType = by
        self._left_col: str = lcon._column.column_name
        self._right_col: str = rcon._column.column_name
        self._compareop = where._compare
        self._context: ClauseContextType = context if context else ClauseInfoContext()

        # COMMENT: When multiple columns reference the same table, we need to create an alias to maintain clear references.
        self._alias: Optional[str] = alias

        self._from_clause = ClauseInfo(self.right_table, alias_table=alias, context=self._context, dialect=dialect, **kw)
        self._left_table_clause = ClauseInfo(self.left_table, column=self.left_col, alias_clause=None, context=self._create_partial_context(), dialect=dialect, **kw)
        self._right_table_clause = ClauseInfo(self.right_table, column=self.right_col, alias_clause=None, context=self._create_partial_context(), dialect=dialect, **kw)

    def __eq__(self, __value: JoinSelector) -> bool:
        return isinstance(__value, JoinSelector) and self.__hash__() == __value.__hash__()

    def __hash__(self) -> int:
        return hash(
            (
                self.left_table,
                self.right_table,
                self._by,
                self._left_col,
                self._right_col,
                self._compareop,
            )
        )

    def _create_partial_context(self) -> ClauseInfoContext:
        """
        Only use table_context from global context
        """
        if not self._context:
            return ClauseInfoContext()
        return ClauseInfoContext(clause_context=None, table_context=self._context._table_context)

    @classmethod
    def join_selectors(cls, dialect: Dialect, *args: JoinSelector) -> str:
        return "\n".join([x.query(dialect) for x in args])

    def query(self, dialect: Dialect, **kwargs) -> str:
        self._context = ClauseInfoContext(clause_context=None, table_context=self._context._table_context)
        list_ = [
            self._by.value,  # inner join
            self._from_clause.query(dialect, **kwargs),
            "ON",
            self._left_table_clause.query(dialect, **kwargs),
            self._compareop,  # =
            self._right_table_clause.query(dialect, **kwargs),
        ]
        return " ".join([x for x in list_ if x is not None])

    @property
    def left_table(self) -> TLeft:
        return self._orig_table

    @property
    def right_table(self) -> TRight:
        return self._right_table

    @property
    def left_col(self) -> str:
        return self._left_col

    @property
    def right_col(self) -> str:
        return self._right_col

    @property
    def alias(self) -> str:
        return self._alias

    @classmethod
    def sort_join_selectors(cls, joins: set[JoinSelector]) -> tuple[JoinSelector]:
        # FIXME [x]: How to sort when needed because it's not necessary at this point. It is for testing purpouse
        if len(joins) == 1:
            return tuple(joins)

        join_object_map: dict[str, list[JoinSelector]] = defaultdict(list)

        for obj in joins:
            join_object_map[obj.left_table].append(obj)

        graph: dict[Type[Table], list[Type[Table]]] = defaultdict(list)
        for join in joins:
            graph[join.left_table].append(join.right_table)

        sorted_graph = DFSTraversal.sort(graph)[::-1]

        if not sorted_graph:
            return tuple(joins)

        res = []
        for table in sorted_graph:
            tables = join_object_map[table]

            if not tables:
                continue
            res.extend(tables)
        return res


__all__ = ["JoinSelector"]
