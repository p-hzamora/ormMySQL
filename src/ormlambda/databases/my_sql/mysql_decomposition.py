from __future__ import annotations
import typing as tp

from ormlambda import ForeignKey
from ormlambda.common.abstract_classes import DecompositionQueryBase
from ormlambda.common.enums import JoinType
from .clauses import JoinSelector

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
    from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext


class MySQLDecompositionQuery[T: tp.Type[Table], *Ts](DecompositionQueryBase[T, *Ts]):
    def __init__(
        self,
        tables: tuple[T, *Ts],
        lambda_query: tp.Callable[[T], tuple[*Ts]],
        *,
        by: JoinType = JoinType.INNER_JOIN,
        replace_asterisk_char: bool = True,
        joins: tp.Optional[list[IJoinSelector]] = None,
        context:tp.Optional[ClauseInfoContext] = None

    ) -> None:
        super().__init__(
            tables=tables,
            lambda_query=lambda_query,
            by=by,
            replace_asterisk_char=replace_asterisk_char,
            joins=joins,
            context=context
        )

    def stringify_foreign_key(self, sep: str = "\n") -> str:
        sorted_joins = JoinSelector.sort_join_selectors(self._joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def _add_fk_relationship[RTable: tp.Type[Table]](self, foreign_key: ForeignKey[T, RTable]) -> None:
        comparer = foreign_key.resolved_function(self._context)
        join_selector = JoinSelector[T, RTable](comparer, self._by,alias=comparer.right_condition.alias_table)
        join_selector.query
        self._joins.add(join_selector)
        t2 = comparer._right_condition.table
        tables = list(self._tables)
        if t2 not in tables:
            tables.append(t2)
        self._tables = tuple(tables)
        return None
