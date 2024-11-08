from __future__ import annotations
import typing as tp

from ormlambda.common.interfaces import IAggregate, ICustomAlias
from ormlambda.common.interfaces.IDecompositionQuery import IDecompositionQuery_one_arg

if tp.TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase


type ClauseDataType = property | str | ICustomAlias


class ClauseInfo[T: tp.Type[Table]](IDecompositionQuery_one_arg[T]):
    @tp.overload
    def __init__(self, table: T, column: property, alias_children_resolver: tp.Callable[..., str]): ...
    @tp.overload
    def __init__(self, table: T, column: str, alias_children_resolver: tp.Callable[..., str]): ...

    def __init__(self, table: T, column: ClauseDataType, alias_children_resolver: tp.Callable[[DecompositionQueryBase[T], str], str]):
        self._table: T = table
        self._row_column: ClauseDataType = column
        self._column: str = self._resolve_column(column)
        self._alias_children_resolver: tp.Callable[[DecompositionQueryBase[T], str], str] = alias_children_resolver
        self._alias: tp.Optional[str] = self._alias_children_resolver(self)

        self._query: str = self.__create_value_string()

    def __repr__(self) -> str:
        return f"{ClauseInfo.__name__}: {self.query}"

    @property
    def table(self) -> T:
        return self._table

    @property
    def column(self) -> ClauseDataType:
        return self._column

    @property
    def alias(self) -> str:
        return self._alias

    @property
    def query(self) -> str:
        return self._query

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        try:
            return self._table.get_column(self.column).dtype
        except ValueError:
            return None

    def _resolve_column(self, data: ClauseDataType) -> str:
        if isinstance(data, property):
            return self._table.__properties_mapped__[data]

        elif isinstance(data, IAggregate):
            return data.alias_name

        elif isinstance(data, str):
            # TODOL: refactor to base the condition in dict with '*' as key. '*' must to work as special character
            return f"'{data}'" if data != DecompositionQueryBase.CHAR else data

        elif isinstance(data, ICustomAlias):
            return data.all_clauses[0].column

        else:
            raise NotImplementedError(f"type of value '{type(data)}' is not implemented.")

    def __create_value_string(self) -> str:
        if isinstance(self._row_column, property):
            return self.concat_with_alias(f"{self._table.table_alias(self._column)}.{self._column}")

        if isinstance(self._row_column, IAggregate):
            return self.concat_with_alias(self._row_column.query)

        return self.concat_with_alias(self.column)

    def concat_with_alias(self, column_name: str) -> str:
        if not self._alias:
            return column_name
        return f"{column_name} as `{self._alias}`"
