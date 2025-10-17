import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Table, Column, ForeignKey  # noqa: E402
from ormlambda import INT, TEXT, DATETIME
from typing import Annotated
from ormlambda import PrimaryKey, AutoIncrement


class A(Table):
    __table_name__ = "a"
    pk_a: Annotated[Column[INT], PrimaryKey(), AutoIncrement()]
    name_a: Column[TEXT]
    data_a: Column[TEXT]
    date_a: Column[DATETIME]
    value: Column[TEXT]


class B(Table):
    __table_name__ = "b"
    pk_b: Annotated[Column[INT], PrimaryKey(), AutoIncrement()]
    data_b: Column[str]
    fk_a: Column[int]
    data: Column[str]

    A = ForeignKey["B", A](A, lambda b, a: b.fk_a == a.pk_a)


class C(Table):
    __table_name__ = "c"
    pk_c: Annotated[Column[INT], PrimaryKey(), AutoIncrement()]
    data_c: Column[str]
    fk_b: Column[int]

    B = ForeignKey["C", B](B, lambda c, b: c.fk_b == b.pk_b)


class ExtraC(Table):
    __table_name__ = "extra_c"
    pk_extra_c: Annotated[Column[int], PrimaryKey()]
    data_extra_c: Column[str]


class D(Table):
    __table_name__ = "d"
    pk_d: Annotated[Column[INT], PrimaryKey(), AutoIncrement()]
    data_d: Column[str]
    fk_c: Column[int]
    fk_extra_c: Column[int]

    C = ForeignKey["D", C](C, lambda self, c: self.fk_c == c.pk_c)
    ExtraC = ForeignKey["D", ExtraC](ExtraC, lambda self, extra_c: self.fk_extra_c == extra_c.pk_extra_c)
