import unittest
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from models import (  # noqa: E402
    City,
    Address,
    A,
    B,
    C,
    D,
    Country,
)

from ormlambda.common.errors import UnmatchedLambdaParameterError

from ormlambda.databases.my_sql.clauses.select import Select
from ormlambda.databases.my_sql.clauses import JoinType  # noqa: E402
from ormlambda.databases.my_sql import functions as func
from ormlambda.databases.my_sql.clauses import Count


class TestSelect(unittest.TestCase):
    def test_all_col_with_no_select_list_attr(self):
        q = Select[City](City)

        mssg: str = "SELECT `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update` FROM city"
        self.assertEqual(q.query, mssg)

    def test_all_col_with_select_list_attr(self):
        q = Select[City](City, columns=lambda x: "*")
        mssg: str = "SELECT `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update` FROM city"
        self.assertEqual(q.query, mssg)

    def test_one_col(self):
        q = Select[City](City, columns=lambda c: c.city)
        self.assertEqual(q.query, "SELECT `city`.city AS `city_city` FROM city")

    def test_two_col(self):
        q = Select[City](City, columns=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT `city`.city AS `city_city`, `city`.city_id AS `city_city_id` FROM city")

    def test_three_col(self):
        q = Select[City](City, columns=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT `city`.city AS `city_city`, `city`.last_update AS `city_last_update`, `city`.country_id AS `city_country_id` FROM city")

    def test_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = Select[Address](
            Address,
            lambda a: (
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
            "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update`, `city`.country_id AS `city_country_id`, `address`.city_id AS `address_city_id`, `address`.last_update AS `address_last_update`, `country`.country AS `country_country` FROM address AS `address` INNER JOIN city AS `city` ON `address`.city_id = `city`.city_id INNER JOIN country AS `country` ON `city`.country_id = `country`.country_id",
        )

    def test_cols_from_foreign_keys_NEW_METHOD(self):
        # this response must not be the real one,
        q = Select[Address](
            Address,
            (
                Address,
                Address.City,
                Address.City.Country,
                Address.City.country_id,
                Address.city_id,
                Address.last_update,
                Address.City.Country.country,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update`, `city`.country_id AS `city_country_id`, `address`.city_id AS `address_city_id`, `address`.last_update AS `address_last_update`, `country`.country AS `country_country` FROM address AS `address` INNER JOIN city AS `city` ON `address`.city_id = `city`.city_id INNER JOIN country AS `country` ON `city`.country_id = `country`.country_id",
        )

    def test_all_columns_from_all_tables(self):
        # this response must not be the real one,
        q = Select[Address, City, Country](
            (Address, City, Country),
            columns=lambda a, ci, co: (
                a,
                ci,
                co,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update` FROM address",
        )

    # COMMENT: depricated test. See if it's useful
    # def test_all_columns_from_tables_without_use_all_vars(self):
    #     # this response must not be the real one,
    #     q = Select[Address, City](
    #         (Address, City),
    #         columns=lambda a, ci: (
    #             a,
    #             a.City,
    #             ci.Country,
    #         ),
    #     )
    #     self.assertEqual(
    #         q.query,
    #         "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update` FROM address INNER JOIN city ON `address`.city_id = `city`.city_id INNER JOIN country ON `city`.country_id = `country`.country_id",
    #     )

    def test_d_c_b_a_models_raiseUnmatchedLambdaParameterError(self):
        with self.assertRaises(UnmatchedLambdaParameterError) as err:
            Select[D, C, B, A](
                (D, C, B, A),
                columns=lambda d: (
                    d.C.B,
                    d.data_d,
                    d.C.data_c,
                    d.C.B.data_b,
                    d.C.B.A.data_a,
                ),
            )

        mssg: str = "Unmatched number of parameters in lambda function with the number of tables: Expected 4 parameters but found ('d',)."
        self.assertEqual(str(err.exception), mssg)

    def test_d_c_b_a_models(self):
        q = Select[D, C, B, A](
            D,
            columns=lambda d: (
                d.C.B,
                d.data_d,
                d.C.data_c,
                d.C.B.data_b,
                d.C.B.A.data_a,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT b.pk_b AS `b_pk_b`, b.data_b AS `b_data_b`, b.fk_a AS `b_fk_a`, b.data AS `b_data`, d.data_d AS `d_data_d`, c.data_c AS `c_data_c`, b.data_b AS `b_data_b`, a.data_a AS `a_data_a` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a",
        )

    def test_all_a(self):
        q = Select[A](A)
        self.assertEqual(q.query, "SELECT a.pk_a AS `a_pk_a`, a.name_a AS `a_name_a`, a.data_a AS `a_data_a`, a.date_a AS `a_date_a`, a.value AS `a_value` FROM a")

    def test_all_b(self):
        q = Select[B](B)
        self.assertEqual(q.query, "SELECT b.pk_b AS `b_pk_b`, b.data_b AS `b_data_b`, b.fk_a AS `b_fk_a`, b.data AS `b_data` FROM b")

    def test_all_c(self):
        q = Select[C](C)
        self.assertEqual(q.query, "SELECT c.pk_c AS `c_pk_c`, c.data_c AS `c_data_c`, c.fk_b AS `c_fk_b` FROM c")

    def test_all_d(self):
        q = Select[D](D)
        self.assertEqual(q.query, "SELECT d.pk_d AS `d_pk_d`, d.data_d AS `d_data_d`, d.fk_c AS `d_fk_c`, d.fk_extra_c AS `d_fk_extra_c` FROM d")

    def test_a_b_c_d_e(self):
        q = Select[D](
            D,
            columns=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )

        mssg: str = "SELECT `a`.pk_a AS `a_pk_a`, `a`.name_a AS `a_name_a`, `a`.data_a AS `a_data_a`, `a`.date_a AS `a_date_a`, `a`.value AS `a_value`, `b`.pk_b AS `b_pk_b`, `b`.data_b AS `b_data_b`, `b`.fk_a AS `b_fk_a`, `b`.data AS `b_data`, `c`.pk_c AS `c_pk_c`, `c`.data_c AS `c_data_c`, `c`.fk_b AS `c_fk_b`, `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c` FROM d AS `d` INNER JOIN c AS `c` ON `d`.fk_c = `c`.pk_c INNER JOIN b AS `b` ON `c`.fk_b = `b`.pk_b INNER JOIN a AS `a` ON `b`.fk_a = `a`.pk_a"
        self.assertEqual(q.query, mssg)

    def test_get_involved_table_method_consistency(self):
        q = Select[D](
            D,
            columns=lambda d: (
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

        q = Select[D, C, B, A]((D, C, B, A), columns=_lambda)

        self.assertEqual(q.table, D)
        self.assertEqual(q._tables, (D, C, B, A))

        self.assertTrue(callable(q._query_list))
        self.assertEqual(q._query_list, _lambda)

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
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_INCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_RIGHT_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.RIGHT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_LEFT_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.LEFT_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d LEFT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_INCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_INCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_FULL_OUTER_EXCLUSIVE_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.FULL_OUTER_EXCLUSIVE)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d RIGHT JOIN c ON d.fk_c = c.pk_c")

    def test_one_col_from_INNER_JOIN_table(self):
        q = Select[D](D, lambda d: d.C.data_c, by=JoinType.INNER_JOIN)
        self.assertEqual(q.query, "SELECT c.data_c AS `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_one_column_without_fk(self):
        self.query = Select[D](D, lambda d: (d.pk_d))
        self.assertEqual(self.query.query, "SELECT d.pk_d AS `d_pk_d` FROM d")

    def test_all_column_without_fk(self):
        self.query = Select[D](D, lambda d: (d))
        self.assertEqual(self.query.query, "SELECT d.pk_d AS `d_pk_d`, d.data_d AS `d_data_d`, d.fk_c AS `d_fk_c`, d.fk_extra_c AS `d_fk_extra_c` FROM d")

    def test_two_column_with_one_fk(self):
        self.query = Select[D](D, lambda d: (d.pk_d, d.C.data_c))
        self.assertEqual(self.query.query, "SELECT d.pk_d AS `d_pk_d`, c.data_c AS `c_data_c` FROM d INNER JOIN c ON d.fk_c = c.pk_c")

    def test_all_column_from_all_tables_with_one_fk(self):
        self.query = Select[D](D, lambda d: (d, d.C))
        self.assertEqual(
            self.query.query,
            "SELECT d.pk_d AS `d_pk_d`, d.data_d AS `d_data_d`, d.fk_c AS `d_fk_c`, d.fk_extra_c AS `d_fk_extra_c`, c.pk_c AS `c_pk_c`, c.data_c AS `c_data_c`, c.fk_b AS `c_fk_b` FROM d INNER JOIN c ON d.fk_c = c.pk_c",
        )

    def test_one_column_with_two_fk_in_one_table(self):
        self.query = Select[D](D, lambda d: (d.ExtraC.data_extra_c))
        self.assertEqual(self.query.query, "SELECT extra_c.data_extra_c AS `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_all_column_with_two_fk_in_one_table(self):
        self.query = Select[D](D, lambda d: (d.ExtraC))
        self.assertEqual(self.query.query, "SELECT extra_c.pk_extra_c AS `extra_c_pk_extra_c`, extra_c.data_extra_c AS `extra_c_data_extra_c` FROM d INNER JOIN extra_c ON d.fk_extra_c = extra_c.pk_extra_c")

    def test_select_with_concat(self):
        context = ClauseInfoContext()
        selected = Select[D](
            D,
            lambda d: (
                d,
                d.C.B.A.data_a,
                d.C,
                func.Concat[D]((D.pk_d, "-", D.C.pk_c, "-", D.C.B.pk_b, "-", D.C.B.A, "-", D.C.B.data), alias_clause="concat_pks", context=context),
                Count(D.C.B.A.name_a, context=context),
                func.Max(D.C.B.A.data_a, context=context),
            ),
            context=context,
        )
        query_string: str = "SELECT d.pk_d AS `d_pk_d`, d.data_d AS `d_data_d`, d.fk_c AS `d_fk_c`, d.fk_extra_c AS `d_fk_extra_c`, a.data_a AS `a_data_a`, c.pk_c AS `c_pk_c`, c.data_c AS `c_data_c`, c.fk_b AS `c_fk_b`, CONCAT(d.pk_d, '-', c.pk_c, '-', b.pk_b, '-', a.pk_a, a.name_a, a.data_a, a.date_a, a.value, '-', b.data) AS `concat_pks`, COUNT(a.name_a) AS `count`, MAX(a.data_a) AS `max` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a"
        self.assertEqual(selected.query, query_string)

    def test_select_with_select_inside(self) -> None:
        select = Select[D](
            D,
            lambda d: (
                d.C,
                func.Concat(D.pk_d, "-", D.data_d),
            ),
        )

        query = "SELECT c.pk_c AS `c_pk_c`, c.data_c AS `c_data_c`, c.fk_b AS `c_fk_b`, CONCAT(d.pk_d, '-', d.data_d) AS `CONCAT` FROM d INNER JOIN c ON d.fk_c = c.pk_c"

        self.assertEqual(select.query, query)

    def test_select_with_context(self):
        context = ClauseInfoContext()
        select = Select[D](
            D,
            columns=(
                D.C,
                D.C.B,
                D.C.B.A,
                func.Concat((D.pk_d, "-", D.data_d), context=context),
            ),
            context=context,
        )

        query: str = "SELECT `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, `c_fk_b_pk_b`.pk_b AS `b_pk_b`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `c_fk_b_pk_b`.fk_a AS `b_fk_a`, `c_fk_b_pk_b`.data AS `b_data`, `b_fk_a_pk_a`.pk_a AS `a_pk_a`, `b_fk_a_pk_a`.name_a AS `a_name_a`, `b_fk_a_pk_a`.data_a AS `a_data_a`, `b_fk_a_pk_a`.date_a AS `a_date_a`, `b_fk_a_pk_a`.value AS `a_value`, CONCAT(`d`.pk_d, '-', `d`.data_d) AS `concat` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a"

        self.assertEqual(select.query, query)


if "__main__" == __name__:
    unittest.main()
