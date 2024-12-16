from __future__ import annotations
import abc
import typing as tp
import re

from ormlambda import Table
from ormlambda import Column
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.types import (
    AsteriskType,
    TableType,
    ColumnType,
    AliasType,
)
from ormlambda.common.interfaces import IAggregate
from ormlambda.common.errors import NotKeysInIAggregateError


from .clause_info_context import ClauseInfoContext

ASTERISK: AsteriskType = "*"


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
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp], context: ClauseInfoContext): ...

    def __init__[TProp](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: tp.Optional[ClauseInfoContext] = None,
    ):
        self._table: TableType[T] = table
        self._column: ColumnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = alias_clause
        self._context: tp.Optional[ClauseInfoContext] = context

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": lambda x: self._column_resolver(x),
            "table": lambda x: self._table.__table_name__,
        }

        self._query: str = self._create_query()

    def __repr__(self) -> str:
        return f"{type(self).__name__}: query -> {self.query}"

    @property
    def table(self) -> TableType[T]:
        return self._table

    @table.setter
    def table(self, value: TableType[T]) -> None:
        self._table = value

    @property
    def alias_clause(self) -> tp.Optional[str]:
        alias = self._alias_clause if not (a := self.get_clause_alias()) else a
        return self._clean_alias(self._alias_clause_resolver(alias))

    @alias_clause.setter
    def alias_clause(self, value: str) -> str:
        self._alias_clause = value

    @property
    def alias_table(self) -> tp.Optional[str]:
        alias = self._alias_table if not (a := self.get_table_alias()) else a
        return self._clean_alias(self._alias_table_resolver(alias))

    @alias_table.setter
    def alias_table(self, value: str) -> str:
        self._alias_table = value

    @property
    def column(self) -> str:
        return self._column_resolver(self._column)

    @property
    def context(self) -> tp.Optional[ClauseInfoContext]:
        return self._context

    @staticmethod
    def _clean_alias(alias: tp.Optional[str]) -> str:
        if alias is None:
            return None
        return re.sub("`", "", alias)

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        if isinstance(self._column, Column):
            return self._column.dtype

        if isinstance(self._column, type):
            return self._column
        return type(self._column)

    @property
    def query(self) -> str:
        return self._query

    def _create_query(self) -> str:
        # when passing some value that is not a column name
        if not self.table and not self._alias_clause:
            return self.column

        if not self.table and self._alias_clause:
            # it means that we are passing an object with alias. We should delete '' around the object
            clean_column = self._column.strip("'")
            alias_clause = self._alias_table_resolver(self._alias_clause)
            return self._concat_alias_and_column(clean_column, alias_clause)

        # When passing the Table itself without 'column'
        if self._table and not self._column:
            if not self._alias_table:
                return self._table.__table_name__
            alias_table = self._alias_table_resolver(self._alias_table)
            return self._concat_alias_and_column(self._table.__table_name__, alias_table)

        if self._return_all_columns():
            return self._get_all_columns()
        return self._resolved_table_and_column(self._column)

    def _resolved_table_and_column(self, column: str) -> str:
        table: tp.Optional[str] = self._alias_table_resolver(self._alias_table)
        column: str = self._column_resolver(column)

        table_column = f"{table}.{column}"
        clause_alias = self._alias_clause_resolver(self._alias_clause)
        return self._concat_alias_and_column(table_column, clause_alias)

    def _return_all_columns(self) -> bool:
        condition = self._column is self._table and issubclass(self._column, Table)
        return any(
            [
                self.is_asterisk(self._column),
                condition,
            ]
        )

    @staticmethod
    def is_asterisk(value: tp.Optional[str]) -> bool:
        return isinstance(value, str) and value == ASTERISK

    def _get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return type(self)(
                self._table,
                column,
                self._alias_table,
                self._alias_clause,
            )

        if self._alias_table:
            return self._resolved_table_and_column(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self._table.get_columns()]

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
        return f"{column} AS {alias_clause}"

    def _alias_resolver(self, alias: AliasType[ClauseInfo[T]]):
        if alias is None:
            return None

        if callable(alias):
            clause_name = alias(self)
            return self._alias_clause_resolver(clause_name)

        alias = self._replace_placeholder(alias)
        return self._wrapped_with_quotes(alias)

    def _alias_table_resolver(self, alias_table: AliasType[ColumnType[T]]) -> tp.Optional[str]:
        """
        Show the name of the table if we don't specified alias_table. Otherwise, return the proper alias for that table
        """

        alias = self._alias_resolver(alias_table)

        if not alias:
            alias = self._table.__table_name__ if self._table else None

        if self._context is not None:
            self._context.add_table_to_context(self.table, alias)
        return alias

    def _alias_clause_resolver[T](self, alias_clause: AliasType[ColumnType[T]]) -> tp.Optional[str]:
        alias = self._alias_resolver(alias_clause)
        if not alias:
            return None

        if self._context is not None:
            self._context.add_clause_to_context(self, alias)
        return alias

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
        context: tp.Optional[ClauseInfoContext] = None,
    ):
        super().__init__(
            table=column.table if isinstance(column, ClauseInfo) else None,  # if table is None, the column strings will not wrapped with ''. we need to treat as object not strings
            alias_table=None,
            column=self._join_column(column, context),
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

        alias_clause = self._alias_clause_resolver(self._alias_clause)
        return self._concat_alias_and_column(f"{self.FUNCTION_NAME()}({self.column})", alias_clause)

    @staticmethod
    def _join_column[TProp](column: ClauseInfo | ColumnType[TProp], context: ClauseInfoContext) -> str:
        if isinstance(column, ClauseInfo):
            return column.query
        if isinstance(column, str) or not isinstance(column, tp.Iterable):
            column = (column,)

        all_clauses: list[ClauseInfo] = []
        for col in column:
            table: tp.Optional[Table] = col.table if isinstance(col, Column) else None
            all_clauses.append(ClauseInfo(table, col, context=context))

        return ClauseInfo.join_clauses(all_clauses)
