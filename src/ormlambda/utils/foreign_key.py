from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING, Type
from .lambda_disassembler import Disassembler

if TYPE_CHECKING:
    from .table_constructor import Table


@dataclass
class TableInfo[T1: Table, T2: Table]:
    orig_table: T1
    referenced_table: T2
    relationship: Callable[[T1, T2], bool]


class ForeignKey[Tbl1: Type[Table], Tbl2: Type[Table]]:
    MAPPED: dict[str, dict[str, TableInfo[Tbl1, Tbl2]]] = {}

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
        if orig_table not in cls.MAPPED:
            cls.MAPPED[orig_table] = {referenced_table.__table_name__: TableInfo(None, referenced_table, relationship)}
        else:
            cls.MAPPED[orig_table].update({referenced_table.__table_name__: TableInfo(None, referenced_table, relationship)})

        return None

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        fk:dict[str,TableInfo[Tbl1, Tbl2]] = ForeignKey[Tbl1, Tbl2].MAPPED.get(orig_table.__table_name__, {})
        for table_info in fk.values():
            dissambler: Disassembler = Disassembler(table_info.relationship)
            orig_col: str = dissambler.cond_1.name
            referenced_col: str = dissambler.cond_2.name

            clauses.append(f"FOREIGN KEY ({orig_col}) REFERENCES {table_info.referenced_table.__table_name__}({referenced_col})")
        return clauses
