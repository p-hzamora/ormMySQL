from __future__ import annotations
from typing import override, Type, Callable, TYPE_CHECKING, Optional

from ormlambda.common.enums.join_type import JoinType
from ormlambda.common.interfaces.IAggregate import IAggregate
import shapely as shp


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
        cols: list[str] = []
        for x in self.all_clauses:
            if x.dtype is shp.Point:
                cols.append(x.concat_with_alias(f"ST_AsText({self.table.table_alias()}.{x.column})"))
            else:
                cols.append(x.query)

            
            if isinstance(x._row_column, IAggregate) and x._row_column.has_foreign_keys:
                self._joins.update(x._row_column.fk_relationship)

        col: str = ", ".join(cols)
        query: str = f"{self.CLAUSE} {col} FROM {self.table.__table_name__} AS `{self.table.table_alias()}`"

        if self.has_foreign_keys:
            query += " " + self.stringify_foreign_key(" ")

        return query
