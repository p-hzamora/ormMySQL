from __future__ import annotations
from collections import defaultdict
from typing import override, Optional, TYPE_CHECKING, Type


from ormlambda.utils.module_tree.dfs_traversal import DFSTraversal
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import JoinType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda.common.abstract_classes.comparer import Comparer

# TODOL [x]: Try to import Table module without circular import Error
if TYPE_CHECKING:
    from ormlambda import Table


class JoinSelector[TLeft: Table, TRight: Table](IJoinSelector[TLeft, TRight]):
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

    def __init__(
        self,
        where: Comparer,
        by: JoinType,
        alias: Optional[str] = None,
    ) -> None:
        self._comparer = where
        self._orig_table = where._left_condition.table
        self._right_table = where._right_condition.table
        self._by = by
        self._left_col = where._left_condition._column.column_name
        self._right_col = where._right_condition._column.column_name
        self._compareop = where._compare

        # COMMENT: When multiple columns reference the same table, we need to create an alias to maintain clear references.
        self._alias: Optional[str] = alias

    def __eq__(self, __value: "JoinSelector") -> bool:
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

    @classmethod
    def join_selectors(cls, *args: "JoinSelector") -> str:
        return "\n".join([x.query for x in args])

    @property
    @override
    def query(self) -> str:
        ltable = self.left_table
        rtable = self.right_table

        clause_table_name_join = ClauseInfo[TLeft](rtable, alias_table=self.alias)
        # return f"{self._by.value} {rtable} {alias}ON {left_col} {self._compareop} {right_col}"
        list_ = [
            self._by.value,  # inner join
            clause_table_name_join.query,
            "ON",
            ClauseInfo[TLeft](ltable, column=self.left_col, alias_table="{table}").query,
            self._compareop,  # =
            ClauseInfo[TLeft](rtable, column=self.right_col, alias_table="{table}").query,
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

    @property
    def alias(self) -> str:
        return self._alias
