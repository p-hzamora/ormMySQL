from __future__ import annotations
import typing as tp
import re

from ormlambda import Table
from ormlambda import Column
from ormlambda.sql.types import (
    ASTERISK,
    TableType,
    ColumnType,
    AliasType,
    TypeEngine,
)
from .interface import IClauseInfo
from ormlambda.sql import ForeignKey


from .clause_info_context import ClauseInfoContext, ClauseContextType

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class ReplacePlaceholderError(ValueError):
    def __init__(self, placeholder: str, attribute: str, *args):
        super().__init__(*args)
        self.placeholder: str = placeholder
        self.attr: str = attribute

    def __str__(self):
        return "You cannot use {" + self.placeholder + "} placeholder without using '" + self.attr + "' attribute"


class ClauseInfo[T: Table](IClauseInfo[T]):
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
    @tp.overload
    def __init__(self, table: TableType[T], keep_asterisk: tp.Optional[bool] = ...): ...
    @tp.overload
    def __init__(self, table: TableType[T], preserve_context: tp.Optional[bool] = ...): ...
    @tp.overload
    def __init__[TProp](self, table: TableType[T], dtype: tp.Optional[TProp] = ...): ...

    @tp.overload
    def __init__(self, dialect: Dialect, *args, **kwargs): ...

    def __init__[TProp](
        self,
        table: TableType[T],
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = None,
        context: ClauseContextType = None,
        keep_asterisk: bool = False,
        preserve_context: bool = False,
        dtype: tp.Optional[TProp] = None,
        *,
        dialect: Dialect,
        **kw,
    ):
        if not self.is_table(table):
            column = table if not column else column
            table = self.extract_table(table)

        self._table: TableType[T] = table
        self._column: TableType[T] | ColumnType[TProp] = column
        self._alias_table: tp.Optional[AliasType[ClauseInfo[T]]] = alias_table
        self._alias_clause: tp.Optional[AliasType[ClauseInfo[T]]] = alias_clause
        self._context: ClauseContextType = context if context else ClauseInfoContext()
        self._keep_asterisk: bool = keep_asterisk
        self._preserve_context: bool = preserve_context
        self._dtype = dtype

        self._dialect: Dialect = dialect

        self._placeholderValues: dict[str, tp.Callable[[TProp], str]] = {
            "column": self.replace_column_placeholder,
            "table": self.replace_table_placeholder,
        }

        if not self._preserve_context and (self._context and any([alias_table, alias_clause])):
            self._context.add_clause_to_context(self)

        super().__init__(**kw)

    def __repr__(self) -> str:
        return f"{type(self).__name__}: query -> {self.query(self._dialect)}"

    def replace_column_placeholder[TProp](self, column: ColumnType[TProp]) -> str:
        if not column:
            raise ReplacePlaceholderError("column", "column")
        return self._column_resolver(column)

    def replace_table_placeholder[TProp](self, _: ColumnType[TProp]) -> str:
        if not self.table:
            raise ReplacePlaceholderError("table", "table")
        return self.table.__table_name__

    @property
    def table(self) -> TableType[T]:
        if self.is_foreign_key(self._table):
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

    def replaced_alias(self, value: str) -> tp.Optional[str]:
        return value

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
        if self._dtype is not None:
            return self._dtype

        if isinstance(self._column, Column):
            return self._column.dtype

        if isinstance(self._column, type):
            return self._column
        return type(self._column)

    @property
    def dbtype(self)->tp.Optional[TypeEngine]:
        if self._dtype is not None:
            return self._dtype

        if isinstance(self._column, Column):
            return self._column.dbtype

        if isinstance(self._column, type):
            return self._column
        return type(self._column)

    def query(self, dialect: Dialect, **kwargs) -> str:
        return self._create_query(dialect, **kwargs)

    def _create_query(self, dialect: Dialect, **kwargs) -> str:
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

    def _join_table_and_column[TProp](self, column: ColumnType[TProp]) -> str:
        # FIXME [x]: Study how to deacoplate from mysql database

        caster = self._dialect.caster()

        if self.alias_table:
            table = self._wrapped_with_quotes(self.alias_table)
        else:
            table = self.table.__table_name__

        column: str = self._column_resolver(column)

        table_column = f"{table}.{column}"

        dtype = str if self.is_table(self.dtype) else self.dtype
        wrapped_column = caster.for_value(table_column, dtype).wildcard_to_select(table_column)
        return self._concat_alias_and_column(wrapped_column, self.alias_clause)

    def _return_all_columns(self) -> bool:
        if self._keep_asterisk:
            return False
        if self.is_foreign_key(self._column) or self.is_table(self._column):
            return True

        C1 = self._column is self.table and self.is_table(self._column)
        return any([self.is_asterisk(self._column), C1])

    @staticmethod
    def is_asterisk(value: tp.Optional[str]) -> bool:
        return isinstance(value, str) and value == ASTERISK

    def _get_all_columns(self) -> str:
        def ClauseCreator(column: str) -> ClauseInfo:
            return ClauseInfo(
                table=self.table,
                column=column,
                alias_table=self._alias_table,
                alias_clause=self._alias_clause,
                context=self._context,
                keep_asterisk=self._keep_asterisk,
                dialect=self._dialect,
            )

        if self._alias_table and self._alias_clause:  # We'll add an "*" when we are certain that we have included 'alias_clause' attr
            return self._join_table_and_column(ASTERISK)

        columns: list[ClauseInfo] = [ClauseCreator(column).query(self._dialect) for column in self.table.get_columns()]

        return ", ".join(columns)

    # FIXME [x]: Study how to deacoplate from mysql database
    def _column_resolver[TProp](self, column: ColumnType[TProp]) -> str:
        if isinstance(column, ClauseInfo):
            return column.query(self._dialect)

        if isinstance(column, tp.Iterable) and isinstance(column[0], ClauseInfo):
            return self.join_clauses(column)

        if isinstance(column, Column):
            return column.column_name

        # if we want to pass the name of a column as a string, the 'table' var must not be None
        if self.table and isinstance(self._column, str):
            return self._column

        if self.is_asterisk(column):
            return ASTERISK

        if self.is_table(self._column):
            return self._column.__table_name__

        if self.is_foreign_key(self._column):
            return self._column.tright.__table_name__

        caster = self._dialect.caster()
        casted_value = caster.for_value(column, self.dtype)
        if not self._table:
            # if we haven't some table atrribute, we assume that the user want to retrieve the string_data from caster.
            return casted_value.string_data
        return casted_value.wildcard_to_select()

    def _replace_placeholder(self, string: str) -> str:
        return self._keyRegex.sub(self._replace, string)

    def _replace(self, match: re.Match[str]) -> str:
        key = match.group(1)

        if not (func := self._placeholderValues.get(key, None)):
            return match.group(0)  # No placeholder / value

        return func(self._column)

    def _concat_alias_and_column(self, column: str, alias_clause: tp.Optional[str] = None) -> str:
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
    def join_clauses(clauses: list[ClauseInfo[T]], chr: str = ",", context: tp.Optional[ClauseInfoContext] = None, *, dialect: Dialect) -> str:
        queries: list[str] = []
        for c in clauses:
            if context:
                c.context = context
                c._dialect = dialect
            queries.append(c.query(dialect))

        return f"{chr} ".join(queries)

    @staticmethod
    def _wrapped_with_quotes(string: str) -> str:
        return f"`{string}`"

    @classmethod
    def extract_table(cls, element: ColumnType[T] | TableType[T]) -> tp.Optional[T]:
        if element is None:
            return None

        if cls.is_table(element):
            return element

        if cls.is_foreign_key(element):
            return element.tright

        if isinstance(element, Column):
            return element.table
        return None

    @staticmethod
    def is_table(data: ColumnType | Table | ForeignKey) -> bool:
        return isinstance(data, type) and issubclass(data, Table)

    @staticmethod
    def is_foreign_key(data: ColumnType | Table | ForeignKey) -> bool:
        return isinstance(data, ForeignKey)

    @classmethod
    def is_column(cls, data: tp.Any) -> bool:
        if cls.is_table(data) or cls.is_foreign_key(data) or cls.is_asterisk(data):
            return False
        if isinstance(data, Column):
            return True
        return False
