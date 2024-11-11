from __future__ import annotations
import typing as tp

from ormlambda import ForeignKey
from ormlambda.common.abstract_classes import DecompositionQueryBase
from ormlambda.common.enums import JoinType
from .clauses import JoinSelector

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.interfaces.IJoinSelector import IJoinSelector


class MySQLDecompositionQuery[T: tp.Type[Table], *Ts](DecompositionQueryBase[T, *Ts]):
    def __init__(
        self,
        tables: tuple[T, *Ts],
        lambda_query: tp.Callable[[T], tuple[*Ts]],
        *,
        alias: bool = True,
        alias_name: tp.Optional[str] = None,
        by: JoinType = JoinType.INNER_JOIN,
        replace_asterisk_char: bool = True,
        joins: tp.Optional[list[IJoinSelector]] = None,
    ) -> None:
        super().__init__(
            tables=tables,
            lambda_query=lambda_query,
            alias=alias,
            alias_name=alias_name,
            by=by,
            replace_asterisk_char=replace_asterisk_char,
            joins=joins,
        )

    def stringify_foreign_key(self, sep: str = "\n") -> str:
        sorted_joins = JoinSelector.sort_join_selectors(self._joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def _add_fk_relationship[T1: tp.Type[Table], T2: tp.Type[Table]](self, t1: T1, t2: T2) -> None:
        for relation in ForeignKey.MAPPED[t1.__table_name__].referenced_tables[t2.__table_name__]:
            new_join = JoinSelector[T1, T2](t1, t2, self._by, where=relation.relationship)
            self._joins.add(new_join)

        tables = list(self._tables)
        if t2 not in tables:
            tables.append(t2)
        self._tables = tuple(tables)
        return None
