from typing import Annotated
from ormlambda import Column, Table, PrimaryKey


class _TestTable(Table):
    __table_name__ = "__test_ddbb__.__test_table__"
    Col1: Annotated[Column[int], PrimaryKey()]
    Col2: Column[int]
    Col3: Column[int]
    Col4: Column[int]
    Col5: Column[int]
    Col6: Column[int]
    Col7: Column[int]
    Col8: Column[int]
    Col9: Column[int]
    Col10: Column[int]
    Col11: Column[int]
    Col12: Column[int]
    Col13: Column[int]
    Col14: Column[int]
    Col15: Column[int]
    Col16: Column[int]
    Col17: Column[int]
    Col18: Column[int]
    Col19: Column[int]
    Col20: Column[int]
    Col21: Column[int]
    Col22: Column[int]
    Col23: Column[int]
    Col24: Column[int]
    Col25: Column[int]
