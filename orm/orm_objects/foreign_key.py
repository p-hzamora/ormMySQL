from collections import defaultdict
from typing import Callable, NamedTuple,Type

from .table import Table


class RelationShip[T: Table](NamedTuple):
    col: str
    object: T


class ForeignKey[Tbl1, Tbl2]:
    MAPPED: dict[str, dict[str, Callable[[Tbl1, Tbl2], bool]]] = defaultdict(dict)

    def __new__(
        cls,
        orig_table: str,
        referenced_table: Type[Tbl2],
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> Tbl2:
        cls.add_foreign_key(orig_table, referenced_table, relationship)

        return referenced_table

    @classmethod
    def add_foreign_key(cls, orig_table: str, referenced_table: Table, relationship: Callable[[Tbl1, Tbl2], bool]) -> None:
        cls.MAPPED[orig_table][referenced_table.__table_name__] = relationship
        return None
