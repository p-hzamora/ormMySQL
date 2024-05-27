from collections import defaultdict
from typing import Callable, NamedTuple

from orm.dissambler import Dissambler
from .table import Table


class RelationShip[T: Table](NamedTuple):
    col: str
    object: T


class ForeignKey[Tbl1, Tbl2]:
    MAPPED: dict[str, dict[str, RelationShip]] = defaultdict(dict)

    def __new__(
        cls,
        orig_table: str,
        referenced_table,
        relationship: Callable[[Tbl1, Tbl2], bool],
    )->Tbl2:
        dissambler_functions: Dissambler[Tbl1, Tbl2] = Dissambler[Tbl1, Tbl2](relationship)

        cls.add_foreign_key(orig_table, referenced_table, dissambler_functions)

        return referenced_table

    @classmethod
    def add_foreign_key(cls, orig_table: str, referenced_table: str, relationship: Dissambler[Tbl1, Tbl2]) -> None:
        fk_orig_table = relationship.cond_1.name
        referenced_column = relationship.cond_2.name

        if fk_orig_table in cls.MAPPED[orig_table]:
            raise KeyError(f"'{fk_orig_table}' already in '{orig_table}' table as foregin key")

        cls.MAPPED[orig_table][fk_orig_table] = RelationShip(referenced_column, referenced_table)
        return None
