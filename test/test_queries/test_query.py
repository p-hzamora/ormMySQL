import unittest
import sys
from pathlib import Path
from datetime import datetime


sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm import Table, Column, ForeignKey  # noqa: E402
from orm.orm_objects.queries.query import SQLQuery  # noqa: E402

# class TestQuery(unittest.TestCase):
#     def test_query(self):
#         a = SQLQuery[Address]()
#         address= Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())
#         a.where(address, lambda a: a.city.country.country_id== 4)


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column(is_primary_key=True)
    name_a: str
    data_a: str
    date_a: datetime


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


class TestQuery(unittest.TestCase):
    def test_select_one_column_without_fk(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d.pk_d))
        self.assertEqual(query.build(), "SELECT d.pk_d as `d_pk_d` FROM d")

    def test_select_all_column_without_fk(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d))
        self.assertEqual(query.build(), "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d")

    def test_select_two_column_with_one_fk(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d.pk_d, d.C.data_c))
        self.assertEqual(query.build(), "SELECT d.pk_d as `d_pk_d`, c.data_c as `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_select_all_column_from_all_tables_with_one_fk(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d, d.C))
        self.assertEqual(
            query.build(),
            "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM d INNER JOIN c ON d.fk_c = c.pk_c",
        )

    def test_select_one_column_with_two_fk_in_one_table(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d.ExtraC.data_extra_c))
        self.assertEqual(query.build(), "SELECT extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_select_all_column_with_two_fk_in_one_table(self):
        query = SQLQuery[D]()
        query.select(D, lambda d: (d.ExtraC))
        self.assertEqual(query.build(), "SELECT extra_c.pk_extra_c as `extra_c_pk_extra_c`, extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")


if __name__ == "__main__":
    unittest.main()
