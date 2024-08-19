from collections import defaultdict
from typing import Callable, TYPE_CHECKING, Type
#from .table_constructor import Table
from .lambda_disassembler import Disassembler

if TYPE_CHECKING:
    from .table_constructor import Table


class ForeignKey[Tbl1:Table, Tbl2:Table]:
    MAPPED: dict[Tbl1, dict[Tbl2, Callable[[Tbl1, Tbl2], bool]]] = defaultdict(dict)

    def __new__(
        cls,
        orig_table: str,
        referenced_table: Type[Tbl2],
        relationship: Callable[[Tbl1, Tbl2], bool],
    ) -> Tbl2:
        cls.add_foreign_key(orig_table, referenced_table, relationship)

        return referenced_table

    @classmethod
    def add_foreign_key(cls, orig_table: str, referenced_table: "Table", relationship: Callable[[Tbl1, Tbl2], bool]) -> None:
        cls.MAPPED[orig_table][referenced_table] = relationship
        return None

    @classmethod
    def create_query(cls, orig_table: "Table") -> list[str]:
        clauses: list[str] = []
        for referenced_table, _lambda in ForeignKey[Tbl1, Tbl2].MAPPED[orig_table].items():
            dissambler: Disassembler = Disassembler(_lambda)
            orig_col: str = dissambler.cond_1.name
            referenced_col: str = dissambler.cond_2.name

            clauses.append(f"FOREIGN KEY ({orig_col}) REFERENCES {referenced_table.__table_name__}({referenced_col})")
        return clauses
