from typing import Callable, Type, override

from ormlambda import Table, JoinType, ForeignKey
from ormlambda.databases.my_sql.clauses.joins import JoinSelector
from ormlambda.databases.my_sql.clauses.select import SelectQuery


class CountQuery[T: Type[Table]](SelectQuery[T]):
    CLAUSE: str = "COUNT"

    def __init__(
        self,
        tables: T | tuple[T] = (),
        select_lambda: Callable[[T], None] | None = lambda: None,
        *,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(tables, select_lambda, by=by)

    @override
    @property
    def query(self) -> str:
        query: str = f"{self.SELECT} {self.CLAUSE}(*) FROM {self._first_table.__table_name__}"

        involved_tables = self.get_involved_tables()
        if not involved_tables:
            return query

        sub_query: str = ""
        for l_tbl, r_tbl in involved_tables:
            join = JoinSelector(l_tbl, r_tbl, by=self._by, where=ForeignKey.MAPPED[l_tbl.__table_name__].referenced_tables[r_tbl.__table_name__].relationship)
            sub_query += f" {join.query}"

        query += sub_query
        return query
