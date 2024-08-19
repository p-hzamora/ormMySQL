import sys
from pathlib import Path
from datetime import datetime


sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from ...common.interfaces import IRepositoryBase  # noqa: E402
from src import BaseModel  # noqa: E402
from ...utils import Table, Column, ForeignKey  # noqa: E402


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column(is_primary_key=True)
    name_a: str
    data_a: str
    date_a: datetime
    value: str


class B(Table):
    __table_name__ = "b"
    pk_b: int = Column(is_primary_key=True)
    data_b: str
    fk_a: int
    data: str

    A = ForeignKey["B", A](__table_name__, A, lambda b, a: b.fk_a == a.pk_a)


class C(Table):
    __table_name__ = "c"
    pk_c: int = Column(is_primary_key=True)
    data_c: str
    fk_b: int
    B = ForeignKey["C", B](__table_name__, B, lambda c, b: c.fk_b == b.pk_b)


class ExtraC(Table):
    __table_name__ = "extra_c"
    pk_extra_c: int = Column(is_primary_key=True)
    data_extra_c: str


class D(Table):
    __table_name__ = "d"
    pk_d: int = Column(is_primary_key=True)
    data_d: str
    fk_c: int
    fk_extra_c: int

    C = ForeignKey["D", C](__table_name__, C, lambda self, c: self.fk_c == c.pk_c)
    ExtraC = ForeignKey["D", ExtraC](__table_name__, ExtraC, lambda self, extra_c: self.fk_extra_c == extra_c.pk_extra_c)


class ModelAB[T](BaseModel[T]):
    def __new__[TRepo](cls, model: T, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, model, repository)
