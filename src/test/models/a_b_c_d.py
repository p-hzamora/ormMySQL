from datetime import datetime
import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda import IRepositoryBase  # noqa: E402
from ormlambda import BaseModel  # noqa: E402
from ormlambda import Table, Column, ForeignKey  # noqa: E402


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column(int, is_primary_key=True)
    name_a: str
    data_a: str
    date_a: datetime
    value: str


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


class ModelAB[T, *Ts](BaseModel[T, *Ts]):
    def __new__[TRepo](cls, model: T, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, model, repository)
