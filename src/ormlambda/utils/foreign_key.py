from __future__ import annotations
from typing import Callable, TYPE_CHECKING, NamedTuple, Type, Optional, overload
from .lambda_disassembler import Disassembler

if TYPE_CHECKING:
    from .table_constructor import Table


class ReferencedTable[T1: Type[Table], T2: Type[Table]](NamedTuple):
    obj: T2
    relationship: Callable[[T1, T2], bool]


class TableInfo[T1: Type[Table], T2: Type[Table]]:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, table_object: T1) -> None: ...

    def __init__(self, table_object: Optional[T1] = None) -> None:
        self._table_object: Optional[T1] = table_object
        self._referenced_tables: dict[str, ReferencedTable[T1, T2]] = {}

    def __repr__(self) -> str:
        return f"<{TableInfo.__name__}> class '{self.table_object}' dependent tables -> [{', '.join(tuple(self.referenced_tables))}]"

    @property
    def referenced_tables(self) -> dict[str, ReferencedTable[T1, T2]]:
        return self._referenced_tables

    def update_referenced_tables(self, referenced_table: Type[Table], relationship: Callable[[T1, T2], bool]) -> None:
        self._referenced_tables.update({referenced_table.__table_name__: ReferencedTable[T1, T2](referenced_table, relationship)})

    @property
    def table_object(self) -> Optional[Type[Table]]:
        return self._table_object

    @table_object.setter
    def table_object(self, value: Type[Table]) -> None:
        self._table_object = value

    @property
    def has_relationship(self) -> bool:
        return len(self._referenced_tables) > 0


class ForeignKey[Tbl1: Type[Table], Tbl2: Type[Table]]:
    MAPPED: dict[str, TableInfo[Tbl1, Tbl2]] = {}

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
            cls.MAPPED[orig_table] = TableInfo()

        # if referenced_table not in cls.MAPPED[orig_table]:
        cls.MAPPED[orig_table].update_referenced_tables(referenced_table, relationship)

        return None

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        fk: TableInfo[Tbl1, Tbl2] = ForeignKey[Tbl1, Tbl2].MAPPED[orig_table.__table_name__]
        for referenced_table_obj in fk.referenced_tables.values():
            dissambler: Disassembler = Disassembler(referenced_table_obj.relationship)
            orig_col: str = dissambler.cond_1.name
            referenced_col: str = dissambler.cond_2.name

            clauses.append(f"FOREIGN KEY ({orig_col}) REFERENCES {referenced_table_obj.obj.__table_name__}({referenced_col})")
        return clauses
