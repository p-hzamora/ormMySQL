from __future__ import annotations
import abc
import typing as tp
import re

from ormlambda import Table
from ormlambda import Column
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.types import (
    ASTERISK,
    TableType,
    ColumnType,
    AliasType,
)
from ormlambda.common.interfaces import IAggregate
from ormlambda.common.errors import NotKeysInIAggregateError
from ormlambda.utils.foreign_key import ForeignKey


from .clause_info_context import ClauseInfoContext, ClauseContextType


class ClauseInfo[T: Table](IQuery):
    _keyRegex: re.Pattern = re.compile(r"{([^{}:]+)}")

    @tp.overload
    def __init__(self, table: TableType[T]): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp]): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp], alias_table: AliasType[ClauseInfo[T]] = ..., alias_clause: AliasType[ClauseInfo[T]] = ...): ...
    @tp.overload
    def __init__(self, table: TableType[T], alias_table: AliasType[ClauseInfo[T]] = ..., alias_clause: AliasType[ClauseInfo[T]] = ...): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp], context: ClauseContextType): ...

    def __init__[TProp](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: ClauseContextType = None,
    ):
        self._table: TableType[T] = table
        self._column: ColumnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = alias_clause
        self._context: ClauseContextType = context if context else ClauseInfoContext()

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": lambda x: self._column_resolver(x),
            "table": lambda x: self.table.__table_name__,
        }

        if self._context and any([alias_table, alias_clause]):
            self._context.add_clause_to_context(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}: query -> {self.query}"

    @property
    def table(self) -> TableType[T]:
        if isinstance(self._table, ForeignKey):
            return self._table.tright
        return self._table

    @table.setter
    def table(self, value: TableType[T]) -> None:
        self._table = value

    @property
    def alias_clause(self) -> tp.Optional[str]:
        alias = self._alias_clause if not (a := self.get_clause_alias()) else a
        return self._alias_resolver(alias)

    # TODOL [ ]: if we using this setter, we don't update the _context with the new value. Study if it's necessary
    @alias_clause.setter
    def alias_clause(self, value: str) -> str:
        self._alias_clause = value

    @property
    def alias_table(self) -> tp.Optional[str]:
        alias = self._alias_table if not (a := self.get_table_alias()) else a
        return self._alias_resolver(alias)

    # TODOL [ ]: if we using this setter, we don't update the _context with the new value. Study if it's necessary
    @alias_table.setter
    def alias_table(self, value: str) -> str:
        self._alias_table = value

    @property
    def column(self) -> str:
        return self._column_resolver(self._column)

    @property
    def unresolved_column(self) -> ColumnType:
        return self._column

    @property
    def context(self) -> ClauseContextType:
        return self._context

    @context.setter
    def context(self, value: ClauseInfoContext) -> None:
        self._context = value

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        if isinstance(self._column, Column):
            return self._column.dtype

        if isinstance(self._column, type):
            return self._column
        return type(self._column)

    @property
    def query(self) -> str:
        return self._create_query()

    def _create_query(self) -> str:
        # when passing some value that is not a column name
        if not self.table and not self._alias_clause:
            return self.column

        if not self.table and self._alias_clause:
            # it means that we are passing an object with alias. We should delete '' around the object
            alias_clause = self.alias_clause
            return self._concat_alias_and_column(self._column, alias_clause)

        # When passing the Table itself without 'column'
        if self.table and not self._column:
            if not self._alias_table:
                return self.table.__table_name__
            alias_table = self.alias_table
            return self._concat_alias_and_column(self.table.__table_name__, alias_table)

        if self._return_all_columns():
            return self._get_all_columns()
        return self._join_table_and_column(self._column)

    def _join_table_and_column(self, column: str) -> str:
        if self.alias_table:
            table = self._wrapped_with_quotes(self.alias_table)
        else:
            table = self.table.__table_name__

        column: str = self._column_resolver(column)

        table_column = f"{table}.{column}"
        return self._concat_alias_and_column(table_column, self.alias_clause)

    def _return_all_columns(self) -> bool:
        if isinstance(self._column, ForeignKey):
            return True

        C1 = self._column is self.table and issubclass(self._column, Table)
        return any([self.is_asterisk(self._column), C1])

    @staticmethod
    def is_asterisk(value: tp.Optional[str]) -> bool:
        return isinstance(value, str) and value == ASTERISK

    def _get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return type(self)(
                table=self.table,
                column=column,
                alias_table=self._alias_table,
                alias_clause=self._alias_clause,
                context=self._context,
            )

        if self._alias_table:
            return self._join_table_and_column(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self.table.get_columns()]

        return ", ".join(columns)

    # FIXME [ ]: Study how to deacoplate from mysql database
    def _column_resolver[TProp](self, column: ColumnType[TProp]) -> str:
        from ormlambda.databases.my_sql.casters import MySQLWriteCastBase

        if isinstance(column, ClauseInfo):
            return column.query

        if isinstance(column, tp.Iterable) and isinstance(column[0], ClauseInfo):
            return self.join_clauses(column)

        if isinstance(column, Column):
            return column.column_name

        # if we want to pass the name of a column as a string, the 'table' var must not be None
        if self.table and isinstance(self._column, str):
            return self._column

        if self.is_asterisk(column):
            return ASTERISK
        return MySQLWriteCastBase().resolve(column)

    def _replace_placeholder(self, string: str) -> str:
        return self._keyRegex.sub(self._replace, string)

    def _replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if not (func := self._placeholderValues.get(key, None)):
            return match.group(0)  # No placeholder / value
        return func(self._column)

    def _concat_alias_and_column(self, column: str, alias_clause: tp.Optional[str]) -> str:
        if alias_clause is None:
            return column
        alias = f"{column} AS {self._wrapped_with_quotes(alias_clause)}"
        return alias

    def _alias_resolver(self, alias: AliasType[ClauseInfo[T]]) -> tp.Optional[str]:
        if alias is None:
            return None

        if callable(alias):
            return self._alias_resolver(alias(self))

        return self._replace_placeholder(alias)

    def get_clause_alias(self) -> tp.Optional[str]:
        if not self._context:
            return None
        return self._context.get_clause_alias(self)

    def get_table_alias(self) -> tp.Optional[str]:
        if not self._context:
            return None
        return self._context.get_table_alias(self.table)

    @staticmethod
    def join_clauses(clauses: list[ClauseInfo[T]], chr: str = ",") -> str:
        return f"{chr} ".join([c.query for c in clauses])

    @staticmethod
    def _wrapped_with_quotes(string: str) -> str:
        return f"`{string}`"


class AggregateFunctionBase(ClauseInfo[None], IAggregate):
    def __init__[TProp: Column](
        self,
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[None]]] = None,
        context: ClauseContextType = None,
    ):
        super().__init__(
            table=Table,  # if table is not None, the column strings will not wrapped with ''. we need to treat as object not strings
            alias_table=None,
            column=column,
            alias_clause=alias_clause,
            context=context,
        )

    @staticmethod
    @abc.abstractmethod
    def FUNCTION_NAME() -> str: ...

    @tp.override
    def _create_query(self) -> str:
        # avoid use placeholder when using IAggregate because no make sense.
        if self._alias_clause and (found := self._keyRegex.findall(self._alias_clause)):
            raise NotKeysInIAggregateError(found)

        columns = self._column_resolver(self._column)
        return self._concat_alias_and_column(f"{self.FUNCTION_NAME()}({columns})", self.alias_clause)

    @staticmethod
    def _convert_into_clauseInfo[TProp](columns: ClauseInfo | ColumnType[TProp], context: ClauseContextType) -> list[ClauseInfo]:
        type ClusterType = ColumnType | str | ForeignKey
        dicc_type: dict[ClusterType, tp.Callable[[ClusterType], ClauseInfo]] = {
            Column: lambda column: ClauseInfo(column.table, column, context=context),
            ClauseInfo: lambda column: column,
            ForeignKey: lambda column: ClauseInfo(column.tright, column.tright, context=context),
            "default": lambda column: ClauseInfo(table=None, column=column, context=context),
        }

        all_clauses: list[ClauseInfo] = []
        if isinstance(columns, str) or not isinstance(columns, tp.Iterable):
            columns = (columns,)
        for value in columns:
            all_clauses.append(dicc_type.get(type(value), dicc_type["default"])(value))

        return all_clauses
