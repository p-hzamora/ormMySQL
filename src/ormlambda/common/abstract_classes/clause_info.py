from __future__ import annotations
import typing as tp
import abc
import re

from ormlambda import Table
from ormlambda.common.interfaces.IQueryCommand import IQuery


ASTERISK: AsterikType = "*"


AsterikType = tp.NewType("AsterikType", str)
type columnType[TProp] = TProp | str | property | AsterikType
type AliasType[T] = str | tp.Callable[[T], str]


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...


class ClauseInfo[T: tp.Type[Table]](IQuery):
    _keyRegex: re.Pattern = re.compile(r"{([^{}:]+)}")

    @tp.overload
    def __init__(self, table: T): ...
    @tp.overload
    def __init__[TProp](self, table: T, column: columnType[TProp]): ...
    @tp.overload
    def __init__[TProp](self, table: T, column: columnType[TProp], alias_table: AliasType[columnType[TProp]] = ..., alias_clause: AliasType[columnType[TProp]] = ...): ...
    @tp.overload
    def __init__(self, table: T, *, aggregation_method: IAggregate = ...): ...
    @tp.overload
    def __init__[TProp](self, table: T, *, aggregation_method: IAggregate = ..., alias_table: AliasType[columnType[TProp]] = ..., alias_clause: AliasType[columnType[TProp]] = ...): ...

    def __init__[TProp: property](
        self,
        table: T,
        column: tp.Optional[columnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[columnType[TProp]]] = None,
        alias_clause: tp.Optional[AliasType[columnType[TProp]]] = None,
        aggregation_method: tp.Optional[IAggregate] = None,
    ):
        self._table: T = table
        self._column: columnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[columnType[TProp]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[columnType[TProp]]] = alias_clause
        self._aggregation_method: tp.Optional[IAggregate] = aggregation_method

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": lambda x: self.__column_resolver(x),
            "table": lambda x: self._table.__table_name__,
        }

    def __repr__(self) -> str:
        return f"{ClauseInfo.__name__}: query -> {self.query}"

    @property
    def table(self) -> T:
        return self._table

    @property
    def alias_clause(self) -> tp.Optional[str]:
        return self._alias_clause

    @property
    def alias_table(self) -> tp.Optional[str]:
        return self._alias_table

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        try:
            return self._table.get_column(self._column).dtype
        except ValueError:
            return None

    @property
    def query(self) -> tp.Optional[str]:
        if self._column is None and self._aggregation_method is None:
            return self.__table_resolver()

        if self._aggregation_method:
            agg_query = self._aggregation_method.query
            return self.__concat_with_alias_clause(agg_query)

        if self.__return_all_columns():
            return self.__get_all_columns()

        column = self.__column_resolver(self._column)
        return self.__create_query(column)

    def __return_all_columns(self) -> bool:
        return self._column == ASTERISK or self._column is self._table

    def __get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return ClauseInfo(self._table, column, self._alias_table, self._alias_clause, self._aggregation_method)

        if self._alias_table:
            return self.__create_query(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self._table.get_columns()]

        return ", ".join(columns)

    def __column_resolver[TProp](self, column: columnType[TProp]) -> str:
        if isinstance(column, property):
            return self._table.__properties_mapped__[column]
        return column

    def __create_query(self, column: str) -> str:
        table = self.__table_resolver()
        return self.__concat_with_alias_clause(f"{table}.{column}")

    def __table_resolver(self) -> str:
        """
        Show the name of the table if we don't specified alias_table. Otherwise, return the proper alias for that table
        """
        tname: str = self._table.__table_name__

        if not self._alias_table:
            return tname

        alias = self._alias_table

        if callable(self._alias_table):
            tname = self._alias_table(self)
            alias = self.__replace_placeholder(tname)

        return self.__wrapped_with_quotes(alias)

    def __replace_placeholder(self, string: str) -> str:
        return self._keyRegex.sub(self.__replace, string)

    def __replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if key not in self._placeholderValues:
            return match.group(0)  # No placeholder / value

        func = self._placeholderValues[key]
        return func(self._column)

    def __concat_with_alias_clause(self, column: str) -> str:
        return self.__concat_passing_alias_and_column(column, self._alias_clause)

    def __concat_passing_alias_and_column(self, column: str, alias_clause: str):
        if alias_clause is None:
            return column

        if callable(alias_clause):
            clause_name = self._alias_clause(self)
            return self.__concat_passing_alias_and_column(column, clause_name)

        alias = self.__replace_placeholder(alias_clause)

        return f"{column} AS {self.__wrapped_with_quotes(alias)}"

    @staticmethod
    def join_clauses(clauses: list[ClauseInfo[T]], chr: str = ",") -> str:
        return f"{chr} ".join([c.query for c in clauses])

    @staticmethod
    def __wrapped_with_quotes(string: str) -> str:
        return f"`{string}`"

