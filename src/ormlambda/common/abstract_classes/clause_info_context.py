from __future__ import annotations
import abc
from typing import Literal, Optional, TYPE_CHECKING

from ormlambda import Table
from ormlambda.types import (
    TableType,
)

from ormlambda import Column

if TYPE_CHECKING:
    from ormlambda.common.interfaces import IAggregate
    from .clause_info import ClauseInfo


class IClauseInfo(abc.ABC): ...


AliasChoiceType = Literal["TABLE", "CLAUSE"]


class ClauseInfoContext(IClauseInfo):
    def __init__[TProp](self) -> None:
        self._alias_context: dict[str,ClauseInfo[TProp]] = {}
        self._clause_context: dict[ClauseInfo[TProp], str] = {}

    @property
    def is_empty(self) -> bool:
        return len(self._alias_context) == 0

    def add_clause_to_context[T: Table](self, clause: Optional[ClauseInfo[T]], alias: str) -> None:
        if not clause:
            return None
        value = self.__build_clause(clause)

        if alias not in self._alias_context:
            self._alias_context[alias] = value
        
        if clause not in self._clause_context:
            self._clause_context[value] = alias
        return None

    def get_alias[T: Table](self, table: TableType[T] | Column) -> Optional[str]:
        if not table:
            return None
        key = self.__build_clause(table)
        return self._alias_context.get(key, None)

    def __build_clause[T: Table](self, clause: ClauseInfo[T]) -> None:
        return clause.query

    def has_alias[T: Table](self, value: TableType[T] | Column) -> bool:
        return self.__build_clause(value) in self._alias_context
