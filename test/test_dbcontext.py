import dbcontext as db
from datetime import datetime
from orm import Table, Column, ForeignKey

address = db.Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column(is_primary_key=True)
    name: str
    data: str
    date: datetime


class B(Table):
    __table_name__ = "b"
    pk_b: int = Column(is_primary_key=True)
    data_b: str
    fk_a: int

    a = ForeignKey["B", A](__table_name__, A, lambda b, a: b.fk_a == a.pk_a)


class C(Table):
    __table_name__ = "c"
    pk_c: int = Column(is_primary_key=True)
    data_c: str
    fk_b: int
    b = ForeignKey["C", B](__table_name__, B, lambda c, b: c.fk_b == b.pk_b)


class D(Table):
    __table_name__ = "d"
    pk_d: int = Column(is_primary_key=True)
    data_d: str
    fk_c: int
    c = ForeignKey["D", C](__table_name__, C, lambda d, c: d.fk_c == c.pk_c)


# a = A(1, "pablo", "trabajador", datetime.now())
# b = B(2, "data_b", 1)
# c = C(3, "data_c", 2)
d = D(4, "data_d", 3)

d_instanceaaaaaaa = d
ad_filter = (
    d_instanceaaaaaaa.join(D, C)
    .join(C, B)
    .join(B, A)
    .where(C, lambda c: c.fk_b == 2)
    .where(B, lambda b: b.fk_a == 1)
    .where(A, lambda a: a.name == "pablo")
    .select(d_instanceaaaaaaa, lambda c: c.country)
)


print(ad_filter)
