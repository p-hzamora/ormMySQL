from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, TYPE_CHECKING, Type, Optional, overload

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction
from .lambda_disassembler import Disassembler

if TYPE_CHECKING:
    from .table_constructor import Table


@dataclass
class ReferencedTable[T1: Type[Table], T2: Type[Table]]:
    orig_table: T1
    referenced_table: T2
    relationship: Callable[[T1, T2], bool]

    @property
    def foreign_key_column(self):
        resolved = TreeInstruction(self.relationship).to_list()
        # FIXME [ ]: Avoid access to left col by position
        col_left = resolved[0].nested_element.name
        return col_left


class TableInfo[T1: Type[Table], T2: Type[Table]]:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, table_object: str) -> None: ...
    @overload
    def __init__(self, table_object: T1) -> None: ...

    def __init__(self, table_object: Optional[T1] = None) -> None:
        self._table_name: str = ""
        self._table_object: Optional[T1] = None
        self._fill_table_variable(table_object)
        self._referenced_tables: dict[str, dict[str, ReferencedTable[T1, T2]]] = {}

    def _fill_table_variable(self, table: str | Type[Table]):
        if isinstance(table, str):
            self._table_name = table
        else:
            self._table_name = table.__table_name__
            self._table_object = table

    def __repr__(self) -> str:
        return f"{TableInfo.__name__}: '{self._table_name}' dependent tables -> [{', '.join(tuple(self.referenced_tables))}]"

    @property
    def referenced_tables(self) -> dict[str, list[ReferencedTable[T1, T2]]]:
        return self._referenced_tables

    def update_referenced_tables(self, orig_table: str, referenced_table: Type[Table], relationship: Callable[[T1, T2], bool]) -> None:
        new_references = ReferencedTable[T1, T2](orig_table, referenced_table, relationship)

        referenced_list = self._referenced_tables.get(referenced_table.__table_name__, [])

        if new_references not in referenced_list:
            referenced_list.append(new_references)
            self._referenced_tables[referenced_table.__table_name__] = referenced_list
        return None

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
    __slots__ = (
        "_orig_table",
        "_referenced_table",
        "_relationship",
    )
    MAPPED: dict[str, TableInfo[Tbl1, Tbl2]] = {}

    def __new__(
        cls,
        orig_table: str,
        referenced_table: Type[Tbl2],
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> Tbl2:
        cls.__add_foreign_key(orig_table, referenced_table, relationship)

        self = super().__new__(cls)
        return self

    def __init__(
        self,
        orig_table: str,
        referenced_table: Type[Tbl2],
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> None:
        self._orig_table: str = orig_table
        self._referenced_table: Type[Tbl2] = referenced_table
        self._relationship: Callable[[Tbl1, Tbl2], bool] = relationship

    def __getattr__(self, name: str) -> Any:
        return getattr(self._referenced_table, name)

    def decomposite_fk(self) -> Disassembler[Tbl1, Tbl2]:
        return Disassembler(self._relationship)

    @classmethod
    def __add_foreign_key(cls, orig_table: str, referenced_table: Table, relationship: Callable[[Tbl1, Tbl2], bool]) -> None:
        if orig_table not in cls.MAPPED:
            cls.MAPPED[orig_table] = TableInfo(orig_table)

        # if referenced_table not in cls.MAPPED[orig_table]:
        cls.MAPPED[orig_table].update_referenced_tables(orig_table, referenced_table, relationship)

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
