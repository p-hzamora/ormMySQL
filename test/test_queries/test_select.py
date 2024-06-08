import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.queries.select import SelectQuery, TableColumn  # noqa: E402
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

        self.assertEqual(q.query, "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city")

    def test_select_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City, select_lambda=lambda: "*")
        self.assertEqual(q.query, "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city")

    def test_select_one_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: c.city)
        self.assertEqual(q.query, "SELECT city.city as `city_city` FROM city")

    def test_select_two_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.city_id as `city_city_id` FROM city")

    def test_select_three_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.last_update as `city_last_update`, city.country_id as `city_country_id` FROM city")

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
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update`, city.country_id as `city_country_id`, address.city_id as `address_city_id`, address.last_update as `address_last_update`, country.country as `country_country` FROM address",
        )

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
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update` FROM address",
        )

    def test_select_all_columns_from_tables_without_use_all_vars(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City](
            Address,
            City,
            select_lambda=lambda a, ci: (
                a,
                a.city,
                ci.country,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update` FROM address",
        )

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
        self.assertEqual(
            q.query, "SELECT b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, d.data_d as `d_data_d`, c.data_c as `c_data_c`, b.data_b as `b_data_b`, a.data_a as `a_data_a` FROM d"
        )

    def test_all_a(self):
        q = SelectQuery[A](A)
        self.assertEqual(q.query, "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a` FROM a")

    def test_all_b(self):
        q = SelectQuery[B](B)
        self.assertEqual(q.query, "SELECT b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a` FROM b")

    def test_all_c(self):
        q = SelectQuery[C](C)
        self.assertEqual(q.query, "SELECT c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM c")

    def test_all_d(self):
        q = SelectQuery[D](D)
        self.assertEqual(q.query, "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c` FROM d")

    def test_a_b_c_d_e(self):
        q = SelectQuery[D](
            D,
            select_lambda=lambda d: (
                d.c.b.a,
                d.c.b,
                d.c,
                d,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a`, b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c` FROM d",
        )

    def test_get_involved_table_method_consistency(self):
        q = SelectQuery[D](
            D,
            select_lambda=lambda d: (
                d.c.b.a,
                d.c.b,
                d.c,
                d,
            ),
        )
        queue = q.get_involved_tables()

        tuple_ = tuple([queue.get_nowait() for _ in range(queue.maxsize)])
        self.assertEqual(tuple_, (D, C, B, A))

    def test_check_private_variabels(self):
        def _lambda(d, c, b, a):
            return d, c, b, a

        q = SelectQuery[D, C, B, A](D, C, B, A, select_lambda=_lambda)

        self.assertEqual(q._first_table, D)
        self.assertEqual(q._tables, (D, C, B, A))

        self.assertTrue(callable(q._select_lambda))
        self.assertEqual(q._select_lambda, _lambda)

        self.assertDictEqual(
            q._assign_lambda_variables_to_table(_lambda),
            {
                "d": D,
                "c": C,
                "b": B,
                "a": A,
            },
        )


class TestTableColumn(unittest.TestCase):
    tc = TableColumn(Address, "address_id")

    def test_TableColumn_properties(self):
        self.assertEqual(self.tc.real_column, "address_id")
        self.assertEqual(self.tc.column, "address.address_id as `address_address_id`")
        self.assertEqual(self.tc.alias, "address_address_id")

    def test_check__hash__and__eq__methods(self):
        tuple_all_columns: tuple[TableColumn, ...] = (
            TableColumn(Address, "address_id"),
            TableColumn(Address, "address"),
            TableColumn(Address, "address2"),
            TableColumn(Address, "district"),
            TableColumn(Address, "city_id"),
            TableColumn(Address, "postal_code"),
            TableColumn(Address, "phone"),
            TableColumn(Address, "location"),
            TableColumn(Address, "last_update"),
        )
        list_all_alias: list[str] = [
            "address_address_id",
            "address_address",
            "address_address2",
            "address_district",
            "address_city_id",
            "address_postal_code",
            "address_phone",
            "address_location",
            "address_last_update",
        ]

        self.assertTupleEqual(tuple(TableColumn.all_columns(Address)), tuple_all_columns)
        self.assertListEqual(self.tc.get_all_alias(), list_all_alias)


if "__main__" == __name__:
    unittest.main()
