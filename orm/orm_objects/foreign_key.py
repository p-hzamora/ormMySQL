from collections import defaultdict
from typing import NamedTuple, Callable

from orm.dissambler import Dissambler
from .table import Table


class RelationShip[T: Table](NamedTuple):
    col: str
    object: Table


class ForeignKey[Tbl1: Table, Tbl2: Table]:
    MAPPED: dict[str, list[dict[str, RelationShip]]] = defaultdict(dict)

    def __init__(
        self,
        orig_table: Table,
        referenced_table: Table,
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> None:
        self._orig_table: Tbl1 = orig_table
        self._referenced_table: Tbl2 = referenced_table
        self._dissambler_functions: Dissambler[Tbl1, Tbl2] = Dissambler[Tbl1, Tbl2](relationship)

        rs: RelationShip = RelationShip[Tbl2](self._dissambler_functions.cond_2, referenced_table)
        self._add_fk(self._orig_table.__table_name__, self._dissambler_functions.cond_1.name, rs)

    def __repr__(self) -> str:
        return f"<{ForeignKey.__name__}>: {self._orig_table.__name__}.{self._dissambler_functions.cond_1} {self._dissambler_functions.compare_op} {self._referenced_table.__name__}.{self._dissambler_functions.cond_2}>"

    @classmethod
    def _add_fk(cls, orig_table: str, fk_orig_table: str, relationship: RelationShip) -> None:
        if fk_orig_table in cls.MAPPED[orig_table]:
            raise KeyError(f"'{fk_orig_table}' already in '{orig_table}' table as foregin key")
        cls.MAPPED[orig_table][fk_orig_table] = relationship
