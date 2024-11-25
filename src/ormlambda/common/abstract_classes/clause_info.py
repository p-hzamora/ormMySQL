from __future__ import annotations
import typing as tp
import abc
import re

from ormlambda import Table, Column
from ormlambda.common.interfaces.IQueryCommand import IQuery


ASTERISK: AsteriskType = "*"


type AsteriskType = str
type TableType = tp.Type[Table]
type ColumnType[TProp] = TProp | str | Column | AsteriskType
type AliasType[T] = str | tp.Callable[[T], str]


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...


class ClauseInfo[T: TableType](IQuery):
    _keyRegex: re.Pattern = re.compile(r"{([^{}:]+)}")

    @tp.overload
    def __init__(self, table: T): ...
    @tp.overload
    def __init__[TProp](self, table: T, column: ColumnType[TProp]): ...
    @tp.overload
    def __init__[TProp](self, table: T, column: ColumnType[TProp], alias_table: AliasType[ColumnType[TProp]] = ..., alias_clause: AliasType[ColumnType[TProp]] = ...): ...
    @tp.overload
    def __init__[TProp](self, table: T, alias_table: AliasType[ColumnType[TProp]] = ..., alias_clause: AliasType[ColumnType[TProp]] = ...): ...

    def __init__[TProp: Column](
        self,
        table: T,
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ColumnType[TProp]]] = None,
        alias_clause: tp.Optional[AliasType[ColumnType[TProp]]] = None,
    ):
        self._table: T = table
        self._column: ColumnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[ColumnType[TProp]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[ColumnType[TProp]]] = alias_clause

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": lambda x: self.__column_resolver(x),
            "table": lambda x: self._table.__table_name__,
        }

    def __repr__(self) -> str:
        return f"{ClauseInfo.__name__}: query -> {self.query}"

    @property
    def table(self) -> TableType:
        return self._table

    @property
    def alias_clause(self) -> tp.Optional[str]:
        return self.__clean_alias(self.__alias_clause_resolver(self._alias_clause))

    @property
    def alias_table(self) -> tp.Optional[str]:
        return self.__clean_alias(self.__alias_table_resolver(self._alias_table))

    @staticmethod
    def __clean_alias(alias: tp.Optional[str]) -> str:
        if alias is None:
            return None
        return re.sub("`", "", alias)

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        return self._column.dtype

    @property
    def query(self) -> tp.Optional[str]:
        # When we pass "*" o the Table itself
        if self._column is None:
            return self.__alias_table_resolver(self._alias_table)

        if isinstance(self._column, IAggregate):
            agg_query = self._column.query
            clause_alias = self.__alias_clause_resolver(self._alias_clause)

            return self.__concat_alias_and_column(agg_query, clause_alias)

        if self.__return_all_columns():
            return self.__get_all_columns()

        column = self.__column_resolver(self._column)
        return self.__create_query(column)

    def __return_all_columns(self) -> bool:
        cond1 = isinstance(self._column, str) and self._column == ASTERISK
        cond2 = self._column is self._table
        return any([cond1, cond2])

    def __get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return ClauseInfo(
                self._table,
                column,
                self._alias_table,
                self._alias_clause,
            )

        if self._alias_table:
            return self.__create_query(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self._table.get_columns()]

        return ", ".join(columns)

    def __column_resolver[TProp](self, column: ColumnType[TProp]) -> str:
        if isinstance(column, Column):
            return column.column_name
        return column

    def __create_query(self, column: str) -> str:
        table = self.__alias_table_resolver(self._alias_table)

        column = f"{table}.{column}"
        clause_alias = self.__alias_clause_resolver(self._alias_clause)
        return self.__concat_alias_and_column(column, clause_alias)

    def __replace_placeholder(self, string: str) -> str:
        return self._keyRegex.sub(self.__replace, string)

    def __replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if not (func := self._placeholderValues.get(key, None)):
            return match.group(0)  # No placeholder / value
        return func(self._column)

    def __concat_alias_and_column(self, column: str, alias_clause: tp.Optional[str]):
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

    def __alias_table_resolver(self, alias_table: AliasType[ColumnType[T]]):
        """
        Show the name of the table if we don't specified alias_table. Otherwise, return the proper alias for that table
        """

        alias = self.__alias_resolver(alias_table)
        if not alias:
            return self._table.__table_name__
        return alias

    def __alias_clause_resolver[T](self, alias_clause: AliasType[ColumnType[T]]) -> tp.Optional[str]:
        return self.__alias_resolver(alias_clause)

    @staticmethod
    def join_clauses(clauses: list[ClauseInfo[T]], chr: str = ",") -> str:
        return f"{chr} ".join([c.query for c in clauses])

    @staticmethod
    def __wrapped_with_quotes(string: str) -> str:
        return f"`{string}`"
