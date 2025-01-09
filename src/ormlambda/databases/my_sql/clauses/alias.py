import typing as tp

from ormlambda.types import AliasType, ColumnType
from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda import Table, Column
from ormlambda.utils.foreign_key import ForeignKey


class Alias(ClauseInfo[None]):
    def __init__[TProp](
        self,
        column: tp.Optional[ColumnType[TProp]] = None,
        alias_table: tp.Optional[AliasType[ClauseInfo[None]]] = None,
        alias_clause: tp.Optional[AliasType[ClauseInfo[None]]] = None,
        context=None,
    ):
        super().__init__(
            table=self._extract_table(column),
            column=column,
            alias_table=alias_table,
            alias_clause=alias_clause,
            context=context,
        )

    def _extract_table[TProp](self, obj: ColumnType[TProp]) -> tp.Optional[Table]:
        if isinstance(obj, type) and issubclass(obj, Table):
            return obj

        if isinstance(obj, ForeignKey):
            return obj.tright
        if isinstance(obj, Column):
            return obj.table
        return None
