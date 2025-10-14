from __future__ import annotations
from typing import TYPE_CHECKING

from ormlambda.sql.clause_info import IAggregate

if TYPE_CHECKING:
    from ormlambda.sql.types import ColumnType, AliasType


class IFunction[TProp](IAggregate):
    column: ColumnType[TProp]
    alias: AliasType[TProp]
