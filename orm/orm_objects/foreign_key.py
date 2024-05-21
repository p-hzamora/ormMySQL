from collections import defaultdict
from typing import NamedTuple, Callable

from orm.dissambler import Dissambler
from .table import Table


class RelationShip[T: Table](NamedTuple):
    col: str
    object: Table


class ForeignKey[Tbl1: Table, Tbl2: Table]:
    MAPPED: dict[str, list[dict[str, RelationShip]]] = defaultdict(dict)

    def __new__(
        cls,
        orig_table: Table,
        referenced_table: Table,
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> None:
        cls._orig_table: Tbl1 = orig_table
        cls._referenced_table: Tbl2 = referenced_table
        cls._relationship: Callable[[Tbl1, Tbl2], bool] = relationship

        cls._dissambler_functions: Dissambler = Dissambler(relationship)

        rs: RelationShip = RelationShip[Tbl2](cls._dissambler_functions.cond_2, referenced_table)

        cls.MAPPED[cls._orig_table.__table_name__][cls._referenced_table.__table_name__] = rs

        if cls._dissambler_functions.cond_1 not in cls.MAPPED[cls._orig_table.__table_name__][cls._referenced_table.__table_name__]:
            cls.MAPPED[cls._orig_table.__table_name__][cls._dissambler_functions.cond_1] = RelationShip[Tbl2](cls._dissambler_functions.cond_2, referenced_table)

        return object.__new__(cls)

    def __repr__(self) -> str:
        return f"<{ForeignKey.__name__}>: {self._orig_table.__name__}.{self._dissambler_functions.cond_1} {self._dissambler_functions.compare_op} {self._referenced_table.__name__}.{self._dissambler_functions.cond_2}>"

    # @classmethod
    # def update_fk_dicc(cls) -> None:
    #     ForeignKey.MAPPED[cls._orig_table.__table_name__][cls._orig_column: RelationShip(
    #                 cls._referenced_column,
    #                 cls._referenced_table,
    #     ]
