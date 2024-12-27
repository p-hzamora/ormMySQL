from __future__ import annotations
import typing as tp

from ormlambda.common.abstract_classes import DecompositionQueryBase
from ormlambda.common.enums import JoinType
from .clauses import JoinSelector

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.abstract_classes.clause_info_context import ClauseContextType


class MySQLDecompositionQuery[T: tp.Type[Table], *Ts](DecompositionQueryBase[T, *Ts]):
    def __init__(
        self,
        tables: tuple[T, *Ts],
        columns: tp.Callable[[T], tuple[*Ts]],
        *,
        by: JoinType = JoinType.INNER_JOIN,
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            tables=tables,
            columns=columns,
            by=by,
            context=context,
        )

    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> tp.Optional[str]:
        if not joins:
            return None
        sorted_joins = JoinSelector.sort_join_selectors(joins)
        return f"{sep}".join([join.query for join in sorted_joins])
