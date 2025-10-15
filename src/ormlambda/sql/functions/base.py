from __future__ import annotations

from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.types import ColumnType, AliasType
from ormlambda.sql.functions.interface import IFunction
from ormlambda import util


class AbstractFunction(ClauseElement, IFunction):
    def __init__[TProp](
        self,
        elements: ColumnType[TProp],
        alias: AliasType[ColumnType[TProp]],
    ):
        self.column = elements
        self.alias = alias

    @util.preload_module("ormlambda.sql.comparer")
    def used_columns(self):
        Comparer = util.preloaded.sql_comparer.Comparer
        ComparerCluster = util.preloaded.sql_comparer.ComparerCluster

        if isinstance(self.column, Comparer | ComparerCluster):
            return self.column.used_columns()

        return [self.column]
