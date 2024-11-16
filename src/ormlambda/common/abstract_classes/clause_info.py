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
    _keyRegex: re.Pattern = re.compile(r"{([^{}:]+)(?::([^{}]+))?}")

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
            "column": lambda x: self._column_name_resolver(x),
            "table": lambda x: self._table.__table_name__,
        }

    @property
    def table(self) -> T:
        return self._table

    @property
    def alias(self) -> tp.Optional[str]:
        return self._alias_clause

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        try:
            return self._table.get_column(self._column).dtype
        except ValueError:
            return None

    @property
    def query(self) -> tp.Optional[str]:
        if self._aggregation_method:
            agg_query = self._aggregation_method.query
            return self._concat_with_alias(agg_query)

        if self._return_all_columns():
            return self._get_all_columns()

        column = self._column_name_resolver(self._column)
        return self._create_query(column)

    def _return_all_columns(self) -> bool:
        return self._column == ASTERISK or self._column is self._table

    def _get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return ClauseInfo(self._table, column, self._alias_table, self._alias_clause, self._aggregation_method)

        if self._alias_table:
            return self._create_query(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query for column in self._table.get_columns()]

        return ", ".join(columns)

    def _column_name_resolver[TProp](self, column: columnType[TProp]) -> str:
        if isinstance(column, property):
            return self._table.__properties_mapped__[column]
        return self._column

    def _create_query(self, column: str) -> str:
        table = self._table_resolver()
        return self._concat_with_alias(f"{table}.{column}")

    def _table_resolver(self) -> str:
        tname: str = self._table.__table_name__

        if callable(self._alias_table):
            tname = f"`{self._alias_table(tname)}`"
            return self._keyRegex.sub(self.__replace, tname)

        return tname if not self._alias_table else f"`{self._alias_table}`"

    def __replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if key not in self._placeholderValues:
            return match.group(0)  # No placeholder / value

        func = self._placeholderValues[key]
        return func(self._column)

    def _concat_with_alias(self, column: str) -> str:
        if callable(self._alias_clause):
            alias = self._alias_clause(self._column_name_resolver(self._column))

            # modified if the user used placeholders
            alias = self._keyRegex.sub(self.__replace, alias)
        else:
            alias = self._alias_clause

        alias = f" AS `{alias}`" if self._alias_clause else ""
        return f"{column}{alias}"
