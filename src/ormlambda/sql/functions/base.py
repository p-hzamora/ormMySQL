from __future__ import annotations

from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.comparer import Comparer, ComparerCluster
from ormlambda.sql.functions.interface import IFunction


class AbstractFunction(ClauseElement, IFunction):
    def __init__[TProp](
        self,
        elements: ColumnType[TProp],
        alias: AliasType[ColumnType[TProp]],
    ):
        self.column = elements
        self.alias = alias

    def used_columns(self):
        if isinstance(self.column, Comparer | ComparerCluster):
            return self.column.used_columns()

        return [self.column]
