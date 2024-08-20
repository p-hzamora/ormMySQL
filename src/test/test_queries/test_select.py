import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.ormlambda.databases.my_sql.clauses.select import SelectQuery, TableColumn  # noqa: E402
from src.test.models import (  # noqa: E402
    City,
    Address,
    Country,
)

from src.ormlambda.databases.my_sql.clauses import JoinType  # noqa: E402
from src.test.models import A, B, C, D  # noqa: E402


class TestSelect(unittest.TestCase):
    def test_all_col_with_no_select_list_attr(self):
        q = SelectQuery[City](City)

        self.assertEqual(q.query, "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city")

    def test_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City, select_lambda=lambda: "*")
        self.assertEqual(q.query, "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city")

    def test_one_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: c.city)
        self.assertEqual(q.query, "SELECT city.city as `city_city` FROM city")

    def test_two_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.city_id as `city_city_id` FROM city")

    def test_three_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.last_update as `city_last_update`, city.country_id as `city_country_id` FROM city")

    def test_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = SelectQuery[Address](
            Address,
            select_lambda=lambda a: (
                a,
                a.City,
                a.City.Country,
                a.City.country_id,
                a.city_id,
                a.last_update,
                a.City.Country.country,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update`, city.country_id as `city_country_id`, address.city_id as `address_city_id`, address.last_update as `address_last_update`, country.country as `country_country` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id",
        )

    def test_all_columns_from_all_tables(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City, Country](
            (Address, City, Country),
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

    def test_all_columns_from_tables_without_use_all_vars(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City](
            (Address, City),
            select_lambda=lambda a, ci: (
                a,
                a.City,
                ci.Country,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id",
        )

    def test_d_c_b_a_models(self):
        # a = A(1, "pablo", "trabajador", datetime.now())
        # b = B(2, "data_b", 1)
        # c = C(3, "data_c", 2)
        # d = D(4, "data_d", 3)
        q = SelectQuery[D, C, B, A](
            (D, C, B, A),
            select_lambda=lambda d: (
                d.C.B,
                d.data_d,
                d.C.data_c,
                d.C.B.data_b,
                d.C.B.A.data_a,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, b.data as `b_data`, d.data_d as `d_data_d`, c.data_c as `c_data_c`, b.data_b as `b_data_b`, a.data_a as `a_data_a` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a",
        )

    def test_all_a(self):
        q = SelectQuery[A](A)
        self.assertEqual(q.query, "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a`, a.value as `a_value` FROM a")

    def test_all_b(self):
        q = SelectQuery[B](B)
        self.assertEqual(q.query, "SELECT b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, b.data as `b_data` FROM b")

    def test_all_c(self):
        q = SelectQuery[C](C)
        self.assertEqual(q.query, "SELECT c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM c")

    def test_all_d(self):
        q = SelectQuery[D](D)
        self.assertEqual(q.query, "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d")

    def test_a_b_c_d_e(self):
        q = SelectQuery[D](
            D,
            select_lambda=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a`, a.value as `a_value`, b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, b.data as `b_data`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a",
        )

    def test_get_involved_table_method_consistency(self):
        q = SelectQuery[D](
            D,
            select_lambda=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )
        tuple_ = q.get_involved_tables()

        self.assertTupleEqual(tuple_, ((D, C), (C, B), (B, A)))

    def test_check_private_variabels(self):
        def _lambda(d, c, b, a):
            return d, c, b, a

        q = SelectQuery[D, C, B, A]((D, C, B, A), select_lambda=_lambda)

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

    def test_one_col_from_RIGHT_INCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.RIGHT_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_INCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_RIGHT_EXCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.RIGHT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_EXCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_INCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_EXCLUSIVE_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_INNER_JOIN_table(self):
        q = SelectQuery[D](D, lambda d: d.C.data_c, by=JoinType.INNER_JOIN)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_one_column_without_fk(self):
        self.query = SelectQuery[D](D, lambda d: (d.pk_d))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d` FROM d")

    def test_all_column_without_fk(self):
        self.query = SelectQuery[D](D, lambda d: (d))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d")

    def test_two_column_with_one_fk(self):
        self.query = SelectQuery[D](D, lambda d: (d.pk_d, d.C.data_c))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d`, c.data_c as `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_all_column_from_all_tables_with_one_fk(self):
        self.query = SelectQuery[D](D, lambda d: (d, d.C))
        self.assertEqual(
            self.query.query,
            "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM d INNER JOIN c ON d.fk_c = c.pk_c",
        )

    def test_one_column_with_two_fk_in_one_table(self):
        self.query = SelectQuery[D](D, lambda d: (d.ExtraC.data_extra_c))
        self.assertEqual(self.query.query, "SELECT extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_all_column_with_two_fk_in_one_table(self):
        self.query = SelectQuery[D](D, lambda d: (d.ExtraC))
        self.assertEqual(self.query.query, "SELECT extra_c.pk_extra_c as `extra_c_pk_extra_c`, extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")


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
