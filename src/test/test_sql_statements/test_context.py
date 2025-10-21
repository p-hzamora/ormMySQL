from ormlambda.common.global_checker import GlobalChecker


from ormlambda import Table, Column, ForeignKey  # noqa: E402
from ormlambda.dialects import mysql


DIALECT = mysql.dialect

DDBBNAME = "__test_ddbb__"


class D(Table):
    __table_name__ = "D"

    pk_d: Column[int] = Column(int, is_primary_key=True)
    name: Column[str]


class C(Table):
    __table_name__ = "C"
    pk_c: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    fk_d1: Column[int]
    fk_d2: Column[int]
    name: Column[str]

    D1 = ForeignKey["C", D](D, lambda self, d: self.fk_d1 == d.pk_d)
    D2 = ForeignKey["C", D](D, lambda self, d: self.fk_d2 == d.pk_d)


class B(Table):
    __table_name__ = "B"
    pk_b: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str]
    fk_c1: Column[int]
    fk_c2: Column[int]
    fk_c3: Column[int]

    C1 = ForeignKey["B", C](C, lambda self, c: self.fk_c1 == c.pk_c)
    C2 = ForeignKey["B", C](C, lambda self, c: self.fk_c2 == c.pk_c)
    C3 = ForeignKey["B", C](C, lambda self, c: self.fk_c3 == c.pk_c)


class A(Table):
    __table_name__ = "A"
    pk_a: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    data_a: Column[str]
    fk_b1: Column[int]
    fk_b2: Column[int]
    fk_b3: Column[int]

    B1 = ForeignKey["A", B](B, lambda self, b: self.fk_b1 == b.pk_b)
    B2 = ForeignKey["A", B](B, lambda self, b: self.fk_b2 == b.pk_b)
    B3 = ForeignKey["A", B](B, lambda self, b: self.fk_b3 == b.pk_b)


resolved_proxy = GlobalChecker[A].resolved_callback_object(
    A,
    lambda a: (
        a.B2,
        a.B1.C1,
        a.B2.C2,
        a.B2.C3,
        a.B1.C1.D2.pk_d,
    ),
)

for x in resolved_proxy:
    a = x.get_table_chain()
resolved_proxy
