import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Table, Column, ForeignKey  # noqa: E402
from ormlambda import INT, TEXT, DATETIME


class A(Table):
    __table_name__ = "a"
    pk_a: Column[INT] = Column(INT(), is_primary_key=True)
    name_a: Column[TEXT] = Column(TEXT())
    data_a: Column[TEXT] = Column(TEXT())
    date_a: Column[DATETIME] = Column(DATETIME())
    value: Column[TEXT] = Column(TEXT())


class B(Table):
    __table_name__ = "b"
    pk_b: int = Column(int, is_primary_key=True, is_auto_increment=True)
    data_b: str
    fk_a: int
    data: str

    A = ForeignKey["B", A](A, lambda b, a: b.fk_a == a.pk_a)


class C(Table):
    __table_name__ = "c"
    pk_c: int = Column(int, is_primary_key=True)
    data_c: str = Column(str)
    fk_b: int = Column(int)
    B = ForeignKey["C", B](B, lambda c, b: c.fk_b == b.pk_b)


class ExtraC(Table):
    __table_name__ = "extra_c"
    pk_extra_c: int = Column(int, is_primary_key=True)
    data_extra_c: str


class D(Table):
    __table_name__ = "d"
    pk_d: int = Column(int, is_primary_key=True)
    data_d: str
    fk_c: int
    fk_extra_c: int

    C = ForeignKey["D", C](C, lambda self, c: self.fk_c == c.pk_c)
    ExtraC = ForeignKey["D", ExtraC](ExtraC, lambda self, extra_c: self.fk_extra_c == extra_c.pk_extra_c)
