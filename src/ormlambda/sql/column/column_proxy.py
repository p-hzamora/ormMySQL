from __future__ import annotations
from typing import TYPE_CHECKING, Optional, overload


from ormlambda.sql.column_table_proxy import ColumnTableProxy
from .column import Column
from ormlambda import ConditionType, JoinType
from ormlambda.sql.elements import ClauseElement
from ormlambda import util

if TYPE_CHECKING:
    from ormlambda.sql.types import ColumnType, ComparerType
    from ormlambda.sql.elements import Dialect
    from ormlambda.sql.context import FKChain
    from ormlambda.sql.comparer import Comparer
    from ormlambda.sql.clauses import JoinSelector


class ColumnProxy[TProp](ColumnTableProxy, Column[TProp], ClauseElement):
    __visit_name__ = "column_proxy"
    _column: Column
    _path: FKChain
    alias: Optional[str]

    @overload
    def __init__(self, column: Column[TProp], path: FKChain): ...
    @overload
    def __init__(self, column: Column[TProp], path: FKChain, alias: str): ...

    def __init__(self, column, path, alias=None):
        self._column = column
        self.alias = alias
        super().__init__(path)

    def __str__(self) -> str:
        return self.get_full_chain()

    def __repr__(self) -> str:
        table = self._column.table
        table = table.__table_name__ if table else None

        col = f"{table}.{self._column.column_name}"
        path = self._path.get_path_key()

        return f"{ColumnProxy.__name__}({col if table else self._column.column_name}) {f'Path={path}' if path else ""}"

    def __getattr__(self, name: str):
        # it does not work when comparing methods
        return getattr(self._column, name)

    @util.preload_module("ormlambda.sql.comparer")
    def __comparer_creator(self, other: ColumnType, compare: ComparerType) -> Comparer:
        Comparer = util.preloaded.sql_comparer.Comparer

        return Comparer(self, other, compare)

    def __eq__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.EQUAL.value)

    def __ne__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.NOT_EQUAL.value)

    def __lt__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.LESS_THAN.value)

    def __le__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.LESS_THAN_OR_EQUAL.value)

    def __gt__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.GREATER_THAN.value)

    def __ge__(self, other: ColumnType) -> Comparer:
        return self.__comparer_creator(other, ConditionType.GREATER_THAN_OR_EQUAL.value)

    def __add__(self, other: ColumnType):
        """a + b"""
        return self.__comparer_creator(other, "+")

    def __sub__(self, other: ColumnType):
        """a - b"""
        return self.__comparer_creator(other, "-")

    def __mul__(self, other: ColumnType):
        """a * b"""
        return self.__comparer_creator(other, "*")

    def __truediv__(self, other: ColumnType):
        """a / b"""
        return self.__comparer_creator(other, "/")

    def __floordiv__(self, other: ColumnType):
        """a // b"""
        return self.__comparer_creator(other, "//")

    def __mod__(self, other: ColumnType):
        """a % b"""
        return self.__comparer_creator(other, "%")

    def __pow__(self, other: ColumnType):
        """a ** b"""
        return self.__comparer_creator(other, "**")

    def get_full_chain(self, chr: str = "."):
        alias: list[str] = [self._path.base.__table_name__]

        n = self.number_table_in_chain()

        for i in range(n):
            fk = self._path.steps[i]

            value = fk.clause_name
            alias.append(value)

        # Column name
        alias.append(self._column.column_name)
        return chr.join(alias)

    def get_table_chain(self) -> str:
        return self._path.get_alias()

    def number_table_in_chain(self) -> int:
        return len(self._path.steps)

    @util.preload_module("ormlambda.sql.clauses")
    def get_relations(self, by: JoinType, dialect: Dialect) -> tuple[JoinSelector]:
        JoinSelector = util.preloaded.sql_clauses.JoinSelector

        result: list[JoinSelector] = []
        alias = self._path.base.__table_name__

        for i in range(self.number_table_in_chain()):
            tbl = self._path.steps[i]
            relation = tbl.resolved_function()

            relation.left_condition.alias = alias
            relation.left_condition.path = self._path[:i]

            alias += f"_{tbl.clause_name}"

            relation.right_condition.alias = alias
            relation.right_condition.path = self._path[: i + 1]

            js = JoinSelector(relation, by, alias, dialect=dialect)
            result.append(js)
        return result
