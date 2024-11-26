from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING, Type, Optional, overload

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction
from .lambda_disassembler import Disassembler

if TYPE_CHECKING:
    from .table_constructor import Table


type TypeTable = Type[Table]


@dataclass
class ReferencedTable[T1: TypeTable, T2: TypeTable]:
    orig_table: T1
    referenced_table: T2
    relationship: Callable[[T1, T2], bool]

    @property
    def foreign_key_column(self):
        resolved = TreeInstruction(self.relationship).to_list()
        # FIXME [ ]: Avoid access to left col by position
        col_left = resolved[0].nested_element.name
        return col_left


class TableInfo[T1: TypeTable, T2: TypeTable]:
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

    def _fill_table_variable(self, table: str | TypeTable):
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

    def update_referenced_tables(self, orig_table: str, referenced_table: TypeTable, relationship: Callable[[T1, T2], bool]) -> None:
        new_references = ReferencedTable[T1, T2](orig_table, referenced_table, relationship)

        referenced_list = self._referenced_tables.get(referenced_table.__table_name__, [])

        if new_references not in referenced_list:
            referenced_list.append(new_references)
            self._referenced_tables[referenced_table.__table_name__] = referenced_list
        return None

    @property
    def table_object(self) -> Optional[TypeTable]:
        return self._table_object

    @table_object.setter
    def table_object(self, value: TypeTable) -> None:
        self._table_object = value

    @property
    def has_relationship(self) -> bool:
        return len(self._referenced_tables) > 0


class ForeignKey[TLeft: TypeTable, TRight: TypeTable]:
    MAPPED: dict[str, TableInfo[TLeft, TRight]] = {}

    def __init__(self, tright: TRight, relationship: Callable[[TLeft, TRight], bool]) -> None:
        self.tright: TRight = tright
        self.relationship: Callable[[TLeft, TRight], bool] = relationship

    def __set_name__(self, owner: TLeft, name) -> None:
        self.tleft = owner
        self.clause_name = name
        self.__add_foreign_key(self.tleft, self.tright, self.relationship)

    def __get__(self, obj: Optional[TRight], objtype=None) -> ForeignKey | TRight:
        if not obj:
            return self
        return self.tright

    def __set__(self, obj, value):
        raise AttributeError(f"The {ForeignKey.__name__} '{self.clause_name}' in the '{self.tleft.__table_name__}' table cannot be overwritten.")

    def __getattr__(self, name: str):
        return getattr(self.tright, name)

    def __repr__(self) -> str:
        return f"{ForeignKey.__name__}"

    @classmethod
    def __add_foreign_key(cls, orig_table: str, referenced_table: Table, relationship: Callable[[TLeft, TRight], bool]) -> None:
        if orig_table not in cls.MAPPED:
            cls.MAPPED[orig_table] = TableInfo(orig_table)

        # if referenced_table not in cls.MAPPED[orig_table]:
        cls.MAPPED[orig_table].update_referenced_tables(orig_table, referenced_table, relationship)

        return None

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        fk: TableInfo[TLeft, TRight] = ForeignKey[TLeft, TRight].MAPPED[orig_table.__table_name__]
        for referenced_tables in fk.referenced_tables.values():
            for referenced_table in referenced_tables:
                dissambler: Disassembler = Disassembler(referenced_table.relationship)
                orig_col: str = dissambler.cond_1.name
                referenced_col: str = dissambler.cond_2.name
                clauses.append(f"FOREIGN KEY ({orig_col}) REFERENCES {referenced_table.referenced_table.__table_name__}({referenced_col})")
        return clauses

    def resolved_function(self):
        """ """
        return self.relationship(self.tleft, self.tright)
