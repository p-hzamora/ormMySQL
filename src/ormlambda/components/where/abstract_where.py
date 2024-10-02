from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda import Table

from ormlambda.common.interfaces import IQuery


class AbstractWhere(IQuery):
    WHERE: str = "WHERE"

    @abstractmethod
    def get_involved_tables(self) -> tuple[tuple[Table, Table]]: ...
