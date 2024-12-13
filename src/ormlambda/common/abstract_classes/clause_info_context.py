from __future__ import annotations
import abc
from typing import Literal, Optional, TYPE_CHECKING

from ormlambda import Table
from ormlambda.types import (
    TableType,
)

from ormlambda import Column

if TYPE_CHECKING:
    from .clause_info import ClauseInfo


class IClauseInfo(abc.ABC): ...


AliasChoiceType = Literal["TABLE", "CLAUSE"]

type ClauseAliasKey[T: Table, TProp] = tuple[TableType[T], Column[TProp]]
type TableAliasKey[T: Table] = T

type AliasKey[T: Table, TProp] = ClauseAliasKey[T, TProp] | TableAliasKey[T]


class ClauseInfoContext(IClauseInfo):
    def __init__[T: Table, TProp](self) -> None:
        self._alias_context: dict[str, AliasKey[T, TProp]] = {}
        self._clause_context: dict[ClauseAliasKey[T, TProp], str] = {}
        self._table_context: dict[TableAliasKey[T], str] = {}

    @property
    def is_empty(self) -> bool:
        return len(self._alias_context) == 0

    def add_clause_to_context[T: Table, TProp](self, clause: ClauseInfo[T], alias: str) -> None:
        if not clause:
            return None

        table_col: ClauseAliasKey[T, TProp] = (clause.table, clause.column)
        if table_col not in self._clause_context:
            self.add_alias(table_col, alias)
            self._clause_context[table_col] = alias

    def add_table_to_context[T: Table](self, table: Optional[TableAliasKey[T]], alias: str) -> None:
        if not table:
            return None

        if table not in self._table_context:
            self.add_alias(table, alias)
            self._table_context[table] = alias

    def add_alias[T: Table, TProp](self, key: AliasKey[T, TProp], alias: str) -> None:
        if not key:
            return None

        if alias not in self._alias_context:
            self._alias_context[alias] = key

        return None

    def get_clause_alias[T: Table, TProp](self, clause: ClauseInfo[T]) -> Optional[str]:
        table_col: ClauseAliasKey[T, TProp] = (clause.table, clause.column)
        return self._clause_context.get(table_col, None)

    def get_table_alias[T: Table](self, table: T) -> Optional[str]:
        return self._table_context.get(table, None)
