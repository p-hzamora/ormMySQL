from __future__ import annotations


from ormlambda.sql import ColumnProxy
from ormlambda.sql import TableProxy
from ormlambda.sql.clause_info import AggregateFunctionBase
from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType


type ConcatResponse[TProp] = tuple[str | ColumnType[TProp], ...]


class Concat(ClauseElement):
    __visit_name__ = "concat"


    def __init__[TProp](
        self,
        values: ConcatResponse[TProp],
        alias: AliasType[ColumnType[TProp]] = "concat",
    ) -> None:
    
        self.values = values
        self.alias = alias
        