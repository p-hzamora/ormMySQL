from __future__ import annotations
import abc
import typing as tp

from ormlambda import Table
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.sql.types import (
    TableType,
    ColumnType,
)


from ..clause_info_context import ClauseContextType


class IClauseInfo[T: Table](IQuery):
    @property
    @abc.abstractmethod
    def table(self) -> TableType[T]: ...
    @property
    @abc.abstractmethod
    def alias_clause(self) -> tp.Optional[str]: ...
    @property
    @abc.abstractmethod
    def alias_table(self) -> tp.Optional[str]: ...
    @property
    @abc.abstractmethod
    def column(self) -> str: ...
    @property
    @abc.abstractmethod
    def unresolved_column(self) -> ColumnType: ...
    @property
    @abc.abstractmethod
    def context(self) -> ClauseContextType: ...
    @property
    @abc.abstractmethod
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]: ...
