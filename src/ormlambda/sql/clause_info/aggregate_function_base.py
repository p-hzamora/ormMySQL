from __future__ import annotations
import abc
import typing as tp

from ormlambda import Table
from ormlambda import Column
from ormlambda.sql.types import (
    TableType,
    ColumnType,
    AliasType,
)
from .interface import IAggregate
from ormlambda.common.errors import NotKeysInIAggregateError
from ormlambda.sql import ForeignKey
from ormlambda.sql.table import TableMeta
from .clause_info import ClauseInfo
from .clause_info_context import ClauseContextType

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class AggregateFunctionBase[T: Table](ClauseInfo[T], IAggregate):
    def __init__[TProp: Column](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: ClauseContextType = None,
        keep_asterisk: bool = False,
        preserve_context: bool = False,
        dtype: TProp = None,
        *,
        dialect: Dialect,
        **kw,
    ):
        self._alias_aggregate = alias_clause
        super().__init__(
            table=table,
            column=column,
            alias_table=alias_table,
            context=context,
            keep_asterisk=keep_asterisk,
            preserve_context=preserve_context,
            dtype=dtype,
            dialect=dialect,
            **kw,
        )

    @staticmethod
    @abc.abstractmethod
    def FUNCTION_NAME() -> str: ...

    @classmethod
    def _convert_into_clauseInfo[TypeColumns, TProp](cls, columns: ClauseInfo | ColumnType[TProp], context: ClauseContextType, dialect: Dialect) -> list[ClauseInfo]:
        type DEFAULT = tp.Literal["default"]
        type ClusterType = ColumnType | ForeignKey | DEFAULT

        dicc_type: dict[ClusterType, tp.Callable[[ClusterType], ClauseInfo]] = {
            Column: lambda column: ClauseInfo(column.table, column, context=context, dialect=dialect),
            ClauseInfo: lambda column: column,
            ForeignKey: lambda tbl: ClauseInfo(tbl.tright, tbl.tright, context=context, dialect=dialect),
            TableMeta: lambda tbl: ClauseInfo(tbl, tbl, context=context, dialect=dialect),
            "default": lambda column: ClauseInfo(table=None, column=column, context=context, dialect=dialect),
        }
        all_clauses: list[ClauseInfo] = []
        if isinstance(columns, str) or not isinstance(columns, tp.Iterable):
            columns = (columns,)
        for value in columns:
            all_clauses.append(dicc_type.get(type(value), dicc_type["default"])(value))

        return all_clauses

    @tp.override
    def query(self, dialect: Dialect, **kwargs) -> str:
        wrapped_ci = self.wrapped_clause_info(self)
        if not self._alias_aggregate:
            return wrapped_ci

        return ClauseInfo(
            table=None,
            column=wrapped_ci,
            alias_clause=self._alias_aggregate,
            context=self._context,
            keep_asterisk=self._keep_asterisk,
            preserve_context=self._preserve_context,
            dialect=self._dialect,
        ).query(dialect, **kwargs)

    def wrapped_clause_info(self, ci: ClauseInfo[T]) -> str:
        # avoid use placeholder when using IAggregate because no make sense.
        if self._alias_aggregate and (found := self._keyRegex.findall(self._alias_aggregate)):
            raise NotKeysInIAggregateError(found)

        return f"{self.FUNCTION_NAME()}({ci._create_query(self._dialect)})"
