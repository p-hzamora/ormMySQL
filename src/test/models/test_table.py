from ormlambda import (
    Column,
    Table,
    BaseModel,
)

from ormlambda import IRepositoryBase


class TestTable(Table):
    __table_name__ = "__test_table__"
    Col1: int = Column(int, is_primary_key=True)
    Col2: int
    Col3: int
    Col4: int
    Col5: int
    Col6: int
    Col7: int
    Col8: int
    Col9: int
    Col10: int
    Col11: int
    Col12: int
    Col13: int
    Col14: int
    Col15: int
    Col16: int
    Col17: int
    Col18: int
    Col19: int
    Col20: int
    Col21: int
    Col22: int
    Col23: int
    Col24: int
    Col25: int


class TestTableModel(BaseModel[TestTable]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, TestTable, repository)
