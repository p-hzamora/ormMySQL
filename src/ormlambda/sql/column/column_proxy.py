from __future__ import annotations
from typing import TYPE_CHECKING, Optional, overload


from ormlambda.sql.column_table_proxy import ColumnTableProxy
from ormlambda.sql.context import PATH_CONTEXT
from .column import Column
from ormlambda import ConditionType, JoinType
from ormlambda.sql.elements import ClauseElement


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

        path = f"{table}.{self._column.column_name}"
        return f"{ColumnProxy.__name__}({path if table else self._column.column_name}) Path={self._path.get_path_key()}"

    def __getattr__(self, name: str):
        # it does not work when comparing methods
        return getattr(self._column, name)

    def __comparer_creator(self, other: ColumnType, compare: ComparerType) -> Comparer:
        from ormlambda.sql.comparer import Comparer

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

    def get_full_chain(self,chr:str='.'):
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

    def get_relations(self, by: JoinType, dialect: Dialect) -> tuple[JoinSelector]:
        from ormlambda.sql.clauses import JoinSelector
        from ormlambda.sql.comparer import Comparer

        result: list[JoinSelector] = []
        alias = self._path.base.__table_name__

        for i in range(self.number_table_in_chain()):
            tbl = self._path.steps[i]
            relation = tbl.resolved_function(dialect)

            lcond = ColumnProxy(column=relation._left_condition, path=self._path.parent, alias=alias)

            alias += f"_{tbl.clause_name}"
            rcond = ColumnProxy(column=relation._right_condition, path=self._path, alias=alias)

            comparer = Comparer(left_condition=lcond, right_condition=rcond, compare=relation.compare)
            js = JoinSelector(comparer, by, alias, dialect=dialect)
            PATH_CONTEXT.add_join(js, alias)
            result.append(js)
            js.compile(dialect)
        return result

    def query(self, dialect: Dialect, **kwargs) -> str:
        from ormlambda.sql.clause_info import ClauseInfo

        alias_table = self.get_table_chain()

        params = {"table": self._path.base, "column": self._column.column_name, "alias_table": alias_table if alias_table else "{table}", "alias_clause": self.alias or "{column}", "dtype": self._column.dtype, "dialect": dialect, **kwargs}
        return ClauseInfo(**params).query(dialect)
