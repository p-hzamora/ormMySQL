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
    def __init__(self, tables: tuple[T, *Ts], columns: tp.Callable[[T], tuple[*Ts]], *, by: JoinType = JoinType.INNER_JOIN, replace_asterisk_char: bool = True, joins: tp.Optional[list[IJoinSelector]] = None, context: tp.Optional[ClauseInfoContext] = None) -> None:
        super().__init__(
            tables=tables,
            columns=columns,
            by=by,
            replace_asterisk_char=replace_asterisk_char,
            joins=joins,
            context=context,
        )

    def stringify_foreign_key(self, sep: str = "\n") -> str:
        sorted_joins = JoinSelector.sort_join_selectors(self._joins)
        return f"{sep}".join([join.query for join in sorted_joins])
