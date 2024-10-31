import unittest
import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from models import (  # noqa: E402
    City,
    Address,
    A,
    B,
    C,
    D,
    Country,
)

from ormlambda.common.errors import DifferentTablesAndVariablesError

from ormlambda.databases.my_sql.clauses.select import Select
from ormlambda.databases.my_sql.clauses import JoinType  # noqa: E402
from ormlambda.databases.my_sql import functions as func
from ormlambda.databases.my_sql.clauses import Count


class TestSelect(unittest.TestCase):
    def test_all_col_with_no_select_list_attr(self):
        q = Select[City](City)

        mssg: str = "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city"
        self.assertEqual(q.query, mssg)

    def test_all_col_with_select_list_attr(self):
        q = Select[City](City, lambda_query=lambda x: "*")
        mssg: str = "SELECT city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update` FROM city"
        self.assertEqual(q.query, mssg)

    def test_one_col(self):
        q = Select[City](City, lambda_query=lambda c: c.city)
        self.assertEqual(q.query, "SELECT city.city as `city_city` FROM city")

    def test_two_col(self):
        q = Select[City](City, lambda_query=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.city_id as `city_city_id` FROM city")

    def test_three_col(self):
        q = Select[City](City, lambda_query=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city.city as `city_city`, city.last_update as `city_last_update`, city.country_id as `city_country_id` FROM city")

    def test_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = Select[Address](
            Address,
            lambda_query=lambda a: (
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
        q = Select[Address, City, Country](
            (Address, City, Country),
            lambda_query=lambda a, ci, co: (
                a,
                ci,
                co,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update` FROM address",
        )

    # COMMENT: depricated test. See if it's useful
    # def test_all_columns_from_tables_without_use_all_vars(self):
    #     # this response must not be the real one,
    #     q = Select[Address, City](
    #         (Address, City),
    #         lambda_query=lambda a, ci: (
    #             a,
    #             a.City,
    #             ci.Country,
    #         ),
    #     )
    #     self.assertEqual(
    #         q.query,
    #         "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id",
    #     )

    def test_d_c_b_a_models_raiseDifferentTablesAndVariablesError(self):
        with self.assertRaises(DifferentTablesAndVariablesError) as err:
            Select[D, C, B, A](
                (D, C, B, A),
                lambda_query=lambda d: (
                    d.C.B,
                    d.data_d,
                    d.C.data_c,
                    d.C.B.data_b,
                    d.C.B.A.data_a,
                ),
            )
        self.assertEqual(str(err.exception), str(DifferentTablesAndVariablesError()))

    def test_d_c_b_a_models(self):
        q = Select[D, C, B, A](
            D,
            lambda_query=lambda d: (
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
        q = Select[A](A)
        self.assertEqual(q.query, "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a`, a.value as `a_value` FROM a")

    def test_all_b(self):
        q = Select[B](B)
        self.assertEqual(q.query, "SELECT b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, b.data as `b_data` FROM b")

    def test_all_c(self):
        q = Select[C](C)
        self.assertEqual(q.query, "SELECT c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM c")

    def test_all_d(self):
        q = Select[D](D)
        self.assertEqual(q.query, "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d")

    def test_a_b_c_d_e(self):
        q = Select[D](
            D,
            lambda_query=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )

        mssg: str = "SELECT a.pk_a as `a_pk_a`, a.name_a as `a_name_a`, a.data_a as `a_data_a`, a.date_a as `a_date_a`, a.value as `a_value`, b.pk_b as `b_pk_b`, b.data_b as `b_data_b`, b.fk_a as `b_fk_a`, b.data as `b_data`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a"
        self.assertEqual(q.query, mssg)

    def test_get_involved_table_method_consistency(self):
        q = Select[D](
            D,
            lambda_query=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )
        tuple_ = set(q.tables)

        self.assertSetEqual(tuple_, set([A, B, C, D]))

    def test_check_private_variabels(self):
        def _lambda(d, c, b, a):
            return d, c, b, a

        q = Select[D, C, B, A]((D, C, B, A), lambda_query=_lambda)

        self.assertEqual(q.table, D)
        self.assertEqual(q._tables, (D, C, B, A))

        self.assertTrue(callable(q._lambda_query))
        self.assertEqual(q._lambda_query, _lambda)

        self.assertDictEqual(
            q.alias_cache,
            {
                "*": q._asterik_resolver,
                "d": D,
                "c": C,
                "b": B,
                "a": A,
            },
        )

    def test_one_col_from_RIGHT_INCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.RIGHT_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_INCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_RIGHT_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.RIGHT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_INCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_INNER_JOIN_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.INNER_JOIN)
        self.assertEqual(q.query, "SELECT c.data_c as `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_one_column_without_fk(self):
        self.query = Select[D](D, lambda d: (d.pk_d))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d` FROM d")

    def test_all_column_without_fk(self):
        self.query = Select[D](D, lambda d: (d))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c` FROM d")

    def test_two_column_with_one_fk(self):
        self.query = Select[D](D, lambda d: (d.pk_d, d.C.data_c))
        self.assertEqual(self.query.query, "SELECT d.pk_d as `d_pk_d`, c.data_c as `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_all_column_from_all_tables_with_one_fk(self):
        self.query = Select[D](D, lambda d: (d, d.C))
        self.assertEqual(
            self.query.query,
            "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b` FROM d INNER JOIN c ON d.fk_c = c.pk_c",
        )

    def test_one_column_with_two_fk_in_one_table(self):
        self.query = Select[D](D, lambda d: (d.ExtraC.data_extra_c))
        self.assertEqual(self.query.query, "SELECT extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_all_column_with_two_fk_in_one_table(self):
        self.query = Select[D](D, lambda d: (d.ExtraC))
        self.assertEqual(self.query.query, "SELECT extra_c.pk_extra_c as `extra_c_pk_extra_c`, extra_c.data_extra_c as `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_select(self):
        selected = Select(
            D,
            lambda d: (
                d,
                d.C.B.A.data_a,
                d.C,
                func.Concat[D](
                    D,
                    lambda d: (d.pk_d, "-", d.C.pk_c, "-", d.C.B.pk_b, "-", d.C.B.A, "-", d.C.B.data),
                    alias_name="concat_pks",
                ),
                Count[D](D, lambda x: x.C.B.A.name_a),
                func.Max[D](D, lambda x: x.C.B.A.data_a),
            ),
        )
        query_string: str = "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c`, a.data_a as `a_data_a`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, CONCAT(d.pk_d, '-', c.pk_c, '-', b.pk_b, '-', a.pk_a, a.name_a, a.data_a, a.date_a, a.value, '-', b.data) as `concat_pks`, COUNT(a.name_a) as `count`, MAX(a.data_a) as `max` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a"
        self.assertEqual(selected.query, query_string)

    def test_select_with_select_inside(self) -> None:
        select = Select(
            D,
            lambda d: (
                d.C,
                func.Concat(D, lambda d: (d.pk_d, "-", d.data_d)),
            ),
        )

        query = "SELECT c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, CONCAT(d.pk_d, '-', d.data_d) as `CONCAT` FROM d INNER JOIN c ON d.fk_c = c.pk_c"

        self.assertEqual(select.query, query)


if "__main__" == __name__:
    unittest.main()
