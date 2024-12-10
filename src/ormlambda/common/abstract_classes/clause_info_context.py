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


class IClauseInfo(abc.ABC): ...


AliasChoiceType = Literal["TABLE", "CLAUSE"]


class ClauseInfoContext(IClauseInfo):
    def __init__[T: Table](self) -> None:
        self._context: dict[TableType[T], str] = {}

    @property
    def is_empty(self) -> bool:
        return len(self._context) == 0

    def add_table_to_context[T: Table](self, table: TableType[T] | Column, alias: str) -> None:
        if not table:
            return None
        key = self.__build_key(table)
        if key not in self._context:
            self._context[key] = alias
        return None

    def get_alias[T: Table](self, table: TableType[T] | Column) -> Optional[str]:
        if not table:
            return None
        key = self.__build_key(table)
        return self._context.get(key, None)

    def __build_key[T: Table, TProp](self, prop: TableType[T] | Column[TProp] | IAggregate) -> None:
        if isinstance(prop, Column):
            return f"{prop.table.__table_name__}_{prop.column_name}_alias_clause"
        elif isinstance(prop, type) and issubclass(prop, Table):
            return f"{prop.__table_name__}_alias_table"
        raise ValueError("The 'prop' value must be 'Column' or 'Table'")

    def has_alias[T: Table](self, value: TableType[T] | Column) -> bool:
        return self.__build_key(value) in self._context
