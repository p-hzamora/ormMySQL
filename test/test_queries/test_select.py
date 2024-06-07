import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.queries.select import SelectQuery  # noqa: E402
from test.models import (  # noqa: E402
    City,
    Address,
    Country,
)

from orm import Table, Column, ForeignKey  # noqa: E402


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


class D(Table):
    __table_name__ = "d"
    pk_d: int = Column(is_primary_key=True)
    data_d: str
    fk_c: int
    c = ForeignKey["D", C](__table_name__, C, lambda d, c: d.fk_c == c.pk_c)


class TestQuery(unittest.TestCase):
    def test_select_all_col_with_no_select_list_attr(self):
        q = SelectQuery[City](City)
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City, select_lambda=lambda: "*")
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_one_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: c.city)
        self.assertEqual(q.query, "SELECT city.city FROM city")

    def test_select_two_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city.city, city.city_id FROM city")

    def test_select_three_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city.city, city.last_update, city.country_id FROM city")

    def test_select_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = SelectQuery[Address](
            Address,
            select_lambda=lambda a: (
                a,
                a.city,
                a.city.country,
                a.city.country_id,
                a.city_id,
                a.last_update,
                a.city.country.country,
            ),
        )
        self.assertEqual(q.query, "SELECT address.*, city.*, country.*, city.country_id, address.city_id, address.last_update, country.country FROM address")

    def test_select_all_columns_from_all_tables(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City, Country](
            Address,
            City,
            Country,
            select_lambda=lambda a, ci, co: (
                a,
                ci,
                co,
            ),
        )
        self.assertEqual(q.query, "SELECT address.*, city.*, country.* FROM address")

    def test_select_all_columns_from_tables_without_use_all_vars(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City, Country](
            Address,
            City,
            select_lambda=lambda a, ci: (
                a,
                a.city,
                ci.country,
            ),
        )
        self.assertEqual(q.query, "SELECT address.*, city.*, country.* FROM address")

    def test_d_c_b_a_models(self):
        # a = A(1, "pablo", "trabajador", datetime.now())
        # b = B(2, "data_b", 1)
        # c = C(3, "data_c", 2)
        # d = D(4, "data_d", 3)
        q = SelectQuery[D, C, B, A](
            D,
            C,
            B,
            A,
            select_lambda=lambda d: (
                d.c.b,
                d.data_d,
                d.c.data_c,
                d.c.b.data_b,
                d.c.b.a.data_a,
            ),
        )
        self.assertEqual(q.query, "SELECT b.*, d.data_d, c.data_c, b.data_b, a.data_a FROM d")


if "__main__" == __name__:
    unittest.main()
