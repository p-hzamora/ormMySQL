from __future__ import annotations


from ormlambda.sql.clause_info import IAggregate
from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType


type ConcatResponse[TProp] = tuple[str | ColumnType[TProp], ...]


class Concat(ClauseElement, IAggregate):
    __visit_name__ = "concat"

    def __init__[TProp](
        self,
        values: ConcatResponse[TProp],
        alias: AliasType[ColumnType[TProp]] = "concat",
    ) -> None:
        self.values = values
        self.alias = alias

    def used_columns(self):
        return [x for x in self.values if not isinstance(x, str)]

    @property
    def dtype(self) -> str:
        return str
