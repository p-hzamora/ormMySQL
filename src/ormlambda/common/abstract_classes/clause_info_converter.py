from __future__ import annotations
import typing as tp
from ormlambda import Table

from ormlambda.sql.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
from ormlambda import ForeignKey

from ormlambda.sql.types import AliasType, TableType, ColumnType


class ClauseInfoConverter[T, TProp](tp.Protocol):
    @classmethod
    def convert(cls, data: T, alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[T]]: ...


class ConvertFromAnyType(ClauseInfoConverter[None, None]):
    @classmethod
    def convert(cls, data: tp.Any, alias_table: AliasType = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[None]]:
        return [ClauseInfo[None](table=None, column=data, alias_table=alias_table, alias_clause=kwargs.get("alias", None), context=context, **kwargs)]


class ConvertFromForeignKey[LT: Table, RT: Table](ClauseInfoConverter[RT, None]):
    @classmethod
    def convert(cls, data: ForeignKey[LT, RT], alias_table=None, context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[RT]]:
        return ConvertFromTable[RT].convert(data.tright, data.get_alias(kwargs["dialect"]), context, **kwargs)


class ConvertFromColumn[TProp](ClauseInfoConverter[None, TProp]):
    @classmethod
    def convert(cls, data: ColumnType[TProp], alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[None]]:
        # COMMENT: if the property belongs to the main class, the columnn name in not prefixed. This only done if the property comes from any join.
        attributes = {
            "table": data.table,
            "column": data,
            "alias_table": alias_table,
            "alias_clause": "{table}_{column}",
            "context": context,
        }
        attributes.update(**kwargs)
        clause_info = ClauseInfo(**attributes)
        return [clause_info]


class ConvertFromIAggregate(ClauseInfoConverter[None, None]):
    @classmethod
    def convert(cls, data: AggregateFunctionBase, alias_table=None, context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[None]]:
        return [data]


class ConvertFromTable[T: Table](ClauseInfoConverter[T, None]):
    @classmethod
    def convert(cls, data: T, alias_table: AliasType[ColumnType] = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[T]]:
        """
        if the data is Table, means that we want to retrieve all columns
        """
        return cls._extract_all_clauses(data, alias_table, context, **kwargs)

    @staticmethod
    def _extract_all_clauses(table: TableType[T], alias_table: AliasType[ColumnType], context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[TableType[T]]]:
        # all columns
        column_clauses = []
        for column in table.get_columns():
            column_clauses.extend(ConvertFromColumn.convert(column, alias_table=alias_table, context=context, **kwargs))
        return column_clauses
