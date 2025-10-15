from __future__ import annotations
from typing import Any, Iterable


from ormlambda.sql.functions.interface import IFunction
from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda import ColumnProxy, TableProxy
from ormlambda.common import GlobalChecker

VALID_CONCAT_TYPES = ColumnProxy | str | TableProxy


class Concat[T](ClauseElement, IFunction):
    __visit_name__ = "concat"

    def __init__[TProp](
        self,
        values: tuple[str | ColumnType[TProp] | TableProxy[T], ...],
        alias: AliasType[ColumnType[TProp]] = "concat",
    ) -> None:
        if isinstance(values, TableProxy):
            values = GlobalChecker.parser_object(values, values._table_class)
        if not self.is_valid(values):
            raise ValueError(values)

        self.values = values
        self.alias = alias

    def used_columns(self):
        return [x for x in self.values if not isinstance(x, str)]

    @property
    def dtype(self) -> str:
        return str

    @staticmethod
    def is_valid(values: Any) -> bool:
        if not isinstance(values, Iterable):
            return False
        for val in values:
            if not isinstance(val, VALID_CONCAT_TYPES):
                return False

        return True
