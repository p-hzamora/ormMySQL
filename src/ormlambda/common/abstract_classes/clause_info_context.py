from __future__ import annotations
import abc
from typing import Literal, Optional, TYPE_CHECKING, overload

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
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__[T: Table, TProp](self, clause_context: dict[ClauseAliasKey[T, TProp], str]) -> None: ...
    @overload
    def __init__[T: Table, TProp](self, table_context: dict[TableAliasKey[T], str]) -> None: ...
    @overload
    def __init__[T: Table, TProp](self, clause_context: dict[AliasKey[T, TProp], str]) -> None: ...
    @overload
    def __init__[T: Table, TProp](self, alias_context: dict[str, AliasKey[T, TProp]]) -> None: ...

    def __init__[T: Table, TProp](
        self,
        clause_context: Optional[dict[ClauseAliasKey[T, TProp], str]] = None,
        table_context: Optional[dict[TableAliasKey[T], str]] = None,
        alias_context: Optional[dict[str, AliasKey[T, TProp]]] = None,
    ) -> None:
        self._alias_context: dict[str, AliasKey[T, TProp]] = alias_context if alias_context else {}
        self._clause_context: dict[AliasKey[T, TProp], str] = clause_context if clause_context else {}
        self._table_context: dict[AliasKey[T, TProp], str] = table_context if table_context else {}

    @property
    def is_empty(self) -> bool:
        return len(self._alias_context) == 0

    def add_clause_to_context[T: Table, TProp](self, clause: ClauseInfo[T]) -> None:
        if not clause:
            return None

        if t := clause.table:
            self._add_table_alias(t, clause._alias_table)
        if c := clause.column:
            self._add_clause_alias((t, c, type(clause)), clause._alias_clause)

        return None

    def _add_clause_alias[T: Table, TProp](self, key: AliasKey[T, TProp], alias: str) -> None:
        if not key:
            return None

        if alias not in self._alias_context:
            self._alias_context[alias] = key

        if key not in self._clause_context:
            self._clause_context[key] = alias

        return None

    def _add_table_alias[T: Table, TProp](self, key: AliasKey[T, TProp], alias: str) -> None:
        if not key:
            return None

        if alias not in self._alias_context:
            self._alias_context[alias] = key

        if key not in self._table_context:
            self._table_context[key] = alias

        return None

    def get_clause_alias[T: Table, TProp](self, clause: ClauseInfo[T]) -> Optional[str]:
        table_col: ClauseAliasKey[T, TProp] = (clause.table, clause.column, type(clause))
        return self._clause_context.get(table_col, None)

    def get_table_alias[T: Table](self, table: T) -> Optional[str]:
        return self._table_context.get(table, None)
