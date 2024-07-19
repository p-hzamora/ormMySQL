from collections import defaultdict
from typing import Callable, NamedTuple, Type

from .table import Table
from ..dissambler import Dissambler


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

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []
        for referenced_table, _lambda in ForeignKey.MAPPED[orig_table.__table_name__].items():
            dissambler: Dissambler = Dissambler(_lambda)
            orig_col: str = dissambler.cond_1.name
            referenced_col: str = dissambler.cond_2.name

            clauses.append(f"FOREIGN KEY ({orig_col}) REFERENCES {referenced_table}({referenced_col})")
        return clauses
