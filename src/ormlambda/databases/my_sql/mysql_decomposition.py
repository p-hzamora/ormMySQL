from __future__ import annotations
import typing as tp

from ormlambda.common.abstract_classes import DecompositionQueryBase
from ormlambda.common.enums import JoinType
from ormlambda.utils.foreign_key import ForeignKey
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
        context: ClauseContextType = None,
    ) -> None:
        super().__init__(
            tables=tables,
            columns=columns,
            context=context,
        )

    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n") -> tp.Optional[str]:
        if not joins:
            return None
        sorted_joins = JoinSelector.sort_join_selectors(joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def pop_tables_and_create_joins_from_ForeignKey(self, by: JoinType = JoinType.INNER_JOIN) -> set[JoinSelector]:
        # When we applied filters in any table that we wont select any column, we need to add manually all neccessary joins to achieve positive result.
        if not ForeignKey.stored_calls:
            return None

        joins = set()
        # Always it's gonna be a set of two
        # FIXME [x]: Resolved when we get Compare object instead ClauseInfo. For instance, when we have multiples condition using '&' or '|'
        for _ in range(len(ForeignKey.stored_calls)):
            fk = ForeignKey.stored_calls.pop()
            join = JoinSelector(fk.resolved_function(lambda: self._context), by, context=self._context, alias=fk.alias)
            joins.add(join)
            self._context._add_table_alias(join.right_table, join.alias)

        return joins
