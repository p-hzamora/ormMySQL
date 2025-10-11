from __future__ import annotations
from collections import defaultdict
from typing import override, Optional, TYPE_CHECKING


from ormlambda.util.module_tree.dfs_traversal import DFSTraversal
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import ColumnProxy, JoinType
from ormlambda.sql.comparer import Comparer
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
        return f"{IQuery.__name__}: {self.__class__.__name__} ({self.alias})"

    def __init__(
        self,
        where: Comparer,
        by: JoinType,
        alias: Optional[str] = "{table}",
        *,
        dialect: Dialect,
        **kw,
    ) -> None:
        self.lcon: ColumnProxy = where.left_condition
        self.rcon: ColumnProxy = where.right_condition
        self._comparer: Comparer = where
        self._orig_table: TLeft = self.lcon.table
        self._right_table: TRight = self.rcon.table
        self._by: JoinType = by
        self._left_col: str = self.lcon._column.column_name
        self._right_col: str = self.rcon._column.column_name
        self._compareop = where._compare

        # COMMENT: When multiple columns reference the same table, we need to create an alias to maintain clear references.
        self._alias: Optional[str] = alias

    def __eq__(self, __value: JoinSelector) -> bool:
        return isinstance(__value, JoinSelector) and self.__hash__() == __value.__hash__()

    def __hash__(self) -> int:
        # Only can add the first instance of a JoinsSelector which has the same alias
        return hash(self.alias)

    @classmethod
    def join_selectors(cls, dialect: Dialect, *args: JoinSelector) -> str:
        return "\n".join([x.query(dialect) for x in args])

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

        graph: dict[str, list[str]] = defaultdict(list)
        for join in joins:
            graph[join.alias].append(join.right_table.__table_name__)

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

    @classmethod
    def sort_joins_by_alias(cls, joins: set[JoinSelector]) -> tuple[JoinSelector]:
        # FIXME [x]: How to sort when needed because it's not necessary at this point. It is for testing purpouse
        if len(joins) == 1:
            return tuple(joins)

        join_object_map: dict[str, JoinSelector] = {}

        for obj in joins:
            join_object_map[obj.alias] = obj

        sorted_graph = []

        for alias in sorted([x.alias for x in joins]):
            sorted_graph.append(join_object_map[alias])

        if not sorted_graph:
            return tuple(joins)

        return tuple(sorted_graph)


__all__ = ["JoinSelector"]
