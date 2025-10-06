from __future__ import annotations
import abc
from typing import Optional, Type, TYPE_CHECKING
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.types import (
    TableType,
    ColumnType,
)

if TYPE_CHECKING:
    from ormlambda import Table


class IClauseInfo[T: Table](IQuery):
    @property
    @abc.abstractmethod
    def table(self) -> TableType[T]: ...
    @property
    @abc.abstractmethod
    def alias_clause(self) -> Optional[str]: ...
    @property
    @abc.abstractmethod
    def alias_table(self) -> Optional[str]: ...
    @property
    @abc.abstractmethod
    def column(self) -> str: ...
    @property
    @abc.abstractmethod
    def unresolved_column(self) -> ColumnType: ...
    @property
    @abc.abstractmethod
    def dtype[TProp](self) -> Optional[Type[TProp]]: ...
