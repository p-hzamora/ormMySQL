from __future__ import annotations
import typing as tp
from ormlambda import Table

from ormlambda.sql.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
from ormlambda import ForeignKey

from ormlambda.sql.types import AliasType, TableType, ColumnType

if tp.TYPE_CHECKING:
    from ormlambda.sql import ColumnProxy, TableProxy


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
    def convert(cls, data: ColumnType[TProp], alias_table: AliasType[ColumnType[TProp]] = "{table}", alias_clause:str="{table}_{column}",context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[None]]:
        # COMMENT: if the property belongs to the main class, the columnn name in not prefixed. This only done if the property comes from any join.
        attributes = {
            "table": data.table,
            "column": data,
            "alias_table": alias_table,
            "alias_clause": alias_clause,
            "context": context,
        }
        attributes.update(**kwargs)
        clause_info = ClauseInfo(**attributes)
        return [clause_info]


class ConvertFromColumnProxy[TProp](ClauseInfoConverter[None, TProp]):
    @classmethod
    def convert(cls, data: ColumnProxy, alias_table: AliasType[ColumnType[TProp]] = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[None]]:
        alias_table = data.get_alias()
        alias_clause = f"{alias_table}_{data._column.column_name}"
        return ConvertFromColumn.convert(data._column, alias_table,alias_clause, context, **kwargs)


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


class ConvertFromTableProxy[T: Table](ClauseInfoConverter[T, None]):
    @classmethod
    def convert(cls, data: TableProxy, alias_table: AliasType[ColumnType] = "{table}", context: ClauseContextType = None, **kwargs) -> list[ClauseInfo[T]]:
        return ConvertFromTable.convert(data._table_class, alias_table, context, **kwargs)
