from __future__ import annotations
import typing as tp
import abc
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


ASTERISK: AsteriskType = "*"


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...

    @property
    @abc.abstractmethod
    def alias_clause(self) -> tp.Optional[str]: ...


class ClauseInfo[T: Table](IQuery):
    _keyRegex: re.Pattern = re.compile(r"{([^{}:]+)}")

    @tp.overload
    def __init__(self, table: TableType[T]): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp]): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], column: ColumnType[TProp], alias_table: AliasType[ColumnType[TProp]] = ..., alias_clause: AliasType[ColumnType[TProp]] = ...): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], alias_table: AliasType[ColumnType[TProp]] = ..., alias_clause: AliasType[ColumnType[TProp]] = ...): ...

    def __init__[TProp: Column](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ColumnType[TProp]]] = None,
        alias_clause: tp.Optional[AliasType[ColumnType[TProp]]] = None,
    ):
        self._table: TableType[T] = table
        self._column: ColumnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[ColumnType[TProp]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[ColumnType[TProp]]] = alias_clause

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": lambda x: self.__column_resolver(x),
            "table": lambda x: self._table.__table_name__,
        }

        self._query: str = self.__create_query()

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
        return self.__clean_alias(self.__alias_clause_resolver(self._alias_clause))

    @alias_clause.setter
    def alias_clause(self, value: str) -> str:
        self._alias_clause = value

    @property
    def alias_table(self) -> tp.Optional[str]:
        return self.__clean_alias(self.__alias_table_resolver(self._alias_table))

    @alias_table.setter
    def alias_table(self, value: str) -> str:
        self._alias_table = value

    @property
    def column(self) -> ColumnType:
        return self.__column_resolver(self._column)

    @staticmethod
    def __clean_alias(alias: tp.Optional[str]) -> str:
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

    def __create_query(self) -> str:
        # when passing some value that is not a column name
        if not self.table:
            return self.column

        # When passing the Table itself without 'column'
        if self._table and not self._column:
            if not self._alias_table:
                return self._table.__table_name__
            alias_table = self.__alias_table_resolver(self._alias_table)
            return self.__concat_alias_and_column(self._table.__table_name__, alias_table)

        if isinstance(self._column, IAggregate):
            agg_query = self._column.query
            clause_alias = self.__alias_clause_resolver(self._column.alias_clause)

            return self.__concat_alias_and_column(agg_query, clause_alias)

        if self.__return_all_columns():
            return self.__get_all_columns()
        return self.__resolved_table_and_column(self._column)

    def __resolved_table_and_column(self, column: str) -> str:
        table: tp.Optional[str] = self.__alias_table_resolver(self._alias_table)
        column: str = self.__column_resolver(column)

        table_column = f"{table}.{column}"
        clause_alias = self.__alias_clause_resolver(self._alias_clause)
        return self.__concat_alias_and_column(table_column, clause_alias)

    def __return_all_columns(self) -> bool:
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

    def __get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return type(self)(
                self._table,
                column,
                self._alias_table,
                self._alias_clause,
            )

        if self._alias_table:
            return self.__resolved_table_and_column(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self._table.get_columns()]

        return ", ".join(columns)

    # FIXME [ ]: Study how to deacoplate from mysql database
    def __column_resolver[TProp](self, column: ColumnType[TProp]) -> str:
        from ormlambda.databases.my_sql.casters import MySQLWriteCastBase

        if isinstance(column, Column):
            return column.column_name

        # if we want to pass the name of a column as a string, the 'table' var must not be None
        if self.table and isinstance(self._column, str):
            return self._column

        if self.is_asterisk(column):
            return ASTERISK
        return MySQLWriteCastBase().resolve(column)

    def __replace_placeholder(self, string: str) -> str:
        return self._keyRegex.sub(self.__replace, string)

    def __replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if not (func := self._placeholderValues.get(key, None)):
            return match.group(0)  # No placeholder / value
        return func(self._column)

    def __concat_alias_and_column(self, column: str, alias_clause: tp.Optional[str]) -> str:
        if alias_clause is None:
            return column
        return f"{column} AS {alias_clause}"

    def __alias_resolver(self, alias: AliasType[ColumnType[T]]):
        if alias is None:
            return None

        if callable(alias):
            clause_name = alias(self)
            return self.__alias_clause_resolver(clause_name)

        alias = self.__replace_placeholder(alias)
        return self.__wrapped_with_quotes(alias)

    def __alias_table_resolver(self, alias_table: AliasType[ColumnType[T]]) -> tp.Optional[str]:
        """
        Show the name of the table if we don't specified alias_table. Otherwise, return the proper alias for that table
        """

        alias = self.__alias_resolver(alias_table)
        if not alias:
            return self._table.__table_name__ if self._table else None
        return alias

    def __alias_clause_resolver[T](self, alias_clause: AliasType[ColumnType[T]]) -> tp.Optional[str]:
        return self.__alias_resolver(alias_clause)

    @staticmethod
    def join_clauses(clauses: list[ClauseInfo[T]], chr: str = ",") -> str:
        return f"{chr} ".join([c.query for c in clauses])

    @staticmethod
    def __wrapped_with_quotes(string: str) -> str:
        return f"`{string}`"
