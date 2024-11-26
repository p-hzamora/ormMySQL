from __future__ import annotations
from typing import override, Type, Callable, TYPE_CHECKING, Optional

from ormlambda.common.enums.join_type import JoinType
import shapely as shp

from ormlambda.databases.my_sql.clauses import ST_AsText
from ormlambda.common.abstract_classes.clause_info import ClauseInfo


if TYPE_CHECKING:
    from ormlambda import Table
    from .joins import JoinSelector

from ..mysql_decomposition import MySQLDecompositionQuery


class Select[T: Type[Table], *Ts](MySQLDecompositionQuery[T, *Ts]):
    CLAUSE: str = "SELECT"

    def __init__(
        self,
        tables: tuple[T, *Ts],
        lambda_query: Callable[[T], tuple] = lambda x: x,
        *,
        alias: bool = False,
        alias_name: str | None = None,
        joins: Optional[list[JoinSelector]] = None,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        super().__init__(
            tables,
            lambda_query,
            alias=alias,
            alias_name=alias_name,
            by=by,
            joins=joins,
        )

    # TODOL: see who to deal when we will have to add more mysql methods
    @override
    @property
    def query(self) -> str:
        cols: list[ClauseInfo[T]] = []
        for x in self.all_clauses:
            if x.dtype is shp.Point:
                cols.append(ST_AsText(x))
            else:
                cols.append(x)

            # # FIXME [ ]: refactor ClauseInfo class
            # if isinstance(x, IAggregate) and x._row_column.has_foreign_keys:
            #     self._joins.update(x._row_column.fk_relationship)

        from_clause = "FROM " + ClauseInfo[T](self.table, None, alias_table=self.table.table_alias()).query
        all_cols: str = ClauseInfo[T].join_clauses(cols, ",")

        select_clauses = [
            self.CLAUSE,
            all_cols,
            from_clause,
        ]
        select_clause = " ".join(select_clauses)

        if self.has_foreign_keys:
            select_clause += " " + self.stringify_foreign_key(" ")

        return select_clause
