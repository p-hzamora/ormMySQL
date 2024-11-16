from __future__ import annotations
from collections import defaultdict
from typing import override, Callable, overload, Optional, TYPE_CHECKING, Type


from ormlambda.utils.module_tree.dfs_traversal import DFSTraversal
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import Disassembler
from ormlambda import JoinType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo

# TODOL [x]: Try to import Table module without circular import Error
if TYPE_CHECKING:
    from ormlambda import Table


class JoinSelector[TLeft, TRight](IJoinSelector[TLeft, TRight]):
    __slots__: tuple = (
        "_orig_table",
        "_table_right",
        "_by",
        "_left_col",
        "_right_col",
        "_compareop",
        "_alias",
    )

    @override
    def __repr__(self) -> str:
        table_col_left: str = f"{self._left_table.table_alias()}.{self._left_col}"
        table_col_right: str = f"{self._right_table.table_alias()}.{self._right_col}"

        return f"{IQuery.__name__}: {self.__class__.__name__} ({table_col_left} == {table_col_right})"

    @overload
    def __init__(
        self,
        table_left: TLeft,
        table_right: TRight,
        col_left: str,
        col_right: str,
        by: JoinType,
    ) -> None: ...

    @overload
    def __init__(
        self,
        table_left: TLeft,
        table_right: TRight,
        by: JoinType,
        where: Callable[[TLeft, TRight], bool],
    ) -> None: ...

    def __init__(
        self,
        left_table: Table,
        right_table: Table,
        by: JoinType,
        left_col: Optional[str] = None,
        right_col: Optional[str] = None,
        where: Optional[Callable[[TLeft, TRight], bool]] = None,
    ) -> None:
        self._left_table: Table = left_table
        self._right_table: Table = right_table
        self._by: JoinType = by

        if all(x is None for x in (left_col, right_col, where)):
            raise ValueError("You must specify at least 'where' clausule or ('_left_col',_right_col')")

        if where is None:
            self._left_col: str = left_col
            self._right_col: str = right_col
            self._compareop: str = "="
        else:
            _dis: Disassembler[TLeft, TRight] = Disassembler[TLeft, TRight](where)
            self._left_col: str = _dis.cond_1.name
            self._right_col: str = _dis.cond_2.name
            self._compareop: str = _dis.compare_op

        # COMMENT: When multiple columns reference the same table, we need to create an alias to maintain clear references.
        self._alias: Optional[str] = f"{self._right_table.table_alias()}_{self._left_col}"

    def __eq__(self, __value: "JoinSelector") -> bool:
        return isinstance(__value, JoinSelector) and self.__hash__() == __value.__hash__()

    def __hash__(self) -> int:
        return hash(
            (
                self._left_table,
                self._right_table,
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
        ltable = self._left_table
        rtable = self._right_table

        clause_table_name_join = ClauseInfo[TLeft](ltable, alias_table=self.alias)
        # return f"{self._by.value} {rtable} {alias}ON {left_col} {self._compareop} {right_col}"
        list_ = [
            self._by.value,  # inner join
            clause_table_name_join.query,
            "ON",
            ClauseInfo[TLeft](ltable, column=self.left_col, alias_table=self.left_table.table_alias(), alias_clause=lambda x: "{table}_{column}").query,
            self._compareop,  # =
            ClauseInfo[TLeft](rtable, column=self.right_col, alias_table=clause_table_name_join.alias_table, alias_clause=lambda x: "{table}_{column}").query,
        ]
        return " ".join([x for x in list_ if x is not None])

    @property
    def alias(self) -> str:
        return self._alias

    @alias.setter
    def alias(self, value: str) -> str:
        self._alias = value

    @property
    def left_table(self) -> TLeft:
        return self._left_table

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
            join_object_map[obj._left_table].append(obj)

        graph: dict[Type[Table], list[Type[Table]]] = defaultdict(list)
        for join in joins:
            graph[join._left_table].append(join._right_table)

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
        return self._right_table.__table_name__ + "_" + self._left_col
