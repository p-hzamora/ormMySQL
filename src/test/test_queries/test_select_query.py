import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.statements.query_builder import QueryBuilder
from test.models import (  # noqa: E402
    City,
    Address,
    A,
    B,
    C,
    D,
    Country,
)

from ormlambda.common.errors import UnmatchedLambdaParameterError

from ormlambda import JoinType  # noqa: E402
from ormlambda.sql.clauses.select import Select
from ormlambda.sql import functions as func
from ormlambda.sql.clauses import Count
from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def SelectMySQL[**T](*args: T.args, **kwargs: T.kwargs) -> Select[T]:
    return Select(*args, **kwargs)


class TestSelect(unittest.TestCase):
    def test_all_col_with_no_select_list_attr(self):
        q = SelectMySQL(City)
        mssg: str = "SELECT `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update` FROM city AS `city`"
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), mssg)

    def test_all_col_with_select_list_attr(self):
        q = SelectMySQL(City, columns=lambda x: "*")
        mssg: str = "SELECT `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update` FROM city AS `city`"
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), mssg)

    def test_one_col(self):
        q = SelectMySQL(City, columns=lambda c: c.city)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `city`.city AS `city_city` FROM city AS `city`")

    def test_two_col(self):
        q = SelectMySQL(City, columns=lambda c: (c.city, c.city_id))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `city`.city AS `city_city`, `city`.city_id AS `city_city_id` FROM city AS `city`")

    def test_three_col(self):
        q = SelectMySQL(City, columns=lambda c: (c.city, c.last_update, c.country_id))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `city`.city AS `city_city`, `city`.last_update AS `city_last_update`, `city`.country_id AS `city_country_id` FROM city AS `city`")

    def test_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = SelectMySQL(
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
        select: str = "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `address_city_id_city_id`.city_id AS `city_city_id`, `address_city_id_city_id`.city AS `city_city`, `address_city_id_city_id`.country_id AS `city_country_id`, `address_city_id_city_id`.last_update AS `city_last_update`, `city_country_id_country_id`.country_id AS `country_country_id`, `city_country_id_country_id`.country AS `country_country`, `city_country_id_country_id`.last_update AS `country_last_update`, `address_city_id_city_id`.country_id AS `city_country_id`, `address`.city_id AS `address_city_id`, `address`.last_update AS `address_last_update`, `city_country_id_country_id`.country AS `country_country` FROM address AS `address`"
        joins = set(
            [
                "INNER JOIN city AS `address_city_id_city_id` ON `address`.city_id = `address_city_id_city_id`.city_id",
                "INNER JOIN country AS `city_country_id_country_id` ON `address_city_id_city_id`.country_id = `city_country_id_country_id`.country_id",
            ]
        )
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.select_joins_testing(qb, select, joins)

    def test_cols_from_foreign_keys_NEW_METHOD(self):
        # this response must not be the real one,
        q = SelectMySQL(
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
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)

        select: str = "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `address_city_id_city_id`.city_id AS `city_city_id`, `address_city_id_city_id`.city AS `city_city`, `address_city_id_city_id`.country_id AS `city_country_id`, `address_city_id_city_id`.last_update AS `city_last_update`, `city_country_id_country_id`.country_id AS `country_country_id`, `city_country_id_country_id`.country AS `country_country`, `city_country_id_country_id`.last_update AS `country_last_update`, `address_city_id_city_id`.country_id AS `city_country_id`, `address`.city_id AS `address_city_id`, `address`.last_update AS `address_last_update`, `city_country_id_country_id`.country AS `country_country` FROM address AS `address`"
        joins = set(
            [
                "INNER JOIN city AS `address_city_id_city_id` ON `address`.city_id = `address_city_id_city_id`.city_id",
                "INNER JOIN country AS `city_country_id_country_id` ON `address_city_id_city_id`.country_id = `city_country_id_country_id`.country_id",
            ]
        )
        self.select_joins_testing(qb, select, joins)

    def test_all_columns_from_all_tables(self):
        # this response must not be the real one,
        q = SelectMySQL(
            (Address, City, Country),
            columns=lambda a, ci, co: (a, ci, co),
        )
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(
            qb.query(DIALECT),
            "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update` FROM address AS `address`",
        )

    # COMMENT: depricated test. See if it's useful
    # def test_all_columns_from_tables_without_use_all_vars(self):
    #     # this response must not be the real one,
    #     q = SelectMySQL(
    #         (Address, City),
    #         columns=lambda a, ci: (
    #             a,
    #             a.City,
    #             ci.Country,
    #         ),
    #     )
    #     self.assertEqual(qb         q.compile(DIALECT).string,
    #         "SELECT `address`.address_id AS `address_address_id`, `address`.address AS `address_address`, `address`.address2 AS `address_address2`, `address`.district AS `address_district`, `address`.city_id AS `address_city_id`, `address`.postal_code AS `address_postal_code`, `address`.phone AS `address_phone`, `address`.location AS `address_location`, `address`.last_update AS `address_last_update`, `city`.city_id AS `city_city_id`, `city`.city AS `city_city`, `city`.country_id AS `city_country_id`, `city`.last_update AS `city_last_update`, `country`.country_id AS `country_country_id`, `country`.country AS `country_country`, `country`.last_update AS `country_last_update` FROM address INNER JOIN city ON `address`.city_id = `city`.city_id INNER JOIN country ON `city`.country_id = `country`.country_id",
    #     )

    def test_d_c_b_a_models_raiseUnmatchedLambdaParameterError(self):
        with self.assertRaises(UnmatchedLambdaParameterError) as err:
            SelectMySQL(
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
        q = SelectMySQL(
            D,
            columns=lambda d: (
                d.C.B,
                d.data_d,
                d.C.data_c,
                d.C.B.data_b,
                d.C.B.A.data_a,
            ),
        )
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        select = "SELECT `c_fk_b_pk_b`.pk_b AS `b_pk_b`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `c_fk_b_pk_b`.fk_a AS `b_fk_a`, `c_fk_b_pk_b`.data AS `b_data`, `d`.data_d AS `d_data_d`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `b_fk_a_pk_a`.data_a AS `a_data_a` FROM d AS `d`"
        joins = set(
            [
                "INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c",
                "INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b",
                "INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a",
            ]
        )
        self.select_joins_testing(qb, select, joins)

    def test_all_a(self):
        q = SelectMySQL(A)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `a`.pk_a AS `a_pk_a`, `a`.name_a AS `a_name_a`, `a`.data_a AS `a_data_a`, `a`.date_a AS `a_date_a`, `a`.value AS `a_value` FROM a AS `a`")

    def test_all_b(self):
        q = SelectMySQL(B)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `b`.pk_b AS `b_pk_b`, `b`.data_b AS `b_data_b`, `b`.fk_a AS `b_fk_a`, `b`.data AS `b_data` FROM b AS `b`")

    def test_all_c(self):
        q = SelectMySQL(C)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `c`.pk_c AS `c_pk_c`, `c`.data_c AS `c_data_c`, `c`.fk_b AS `c_fk_b` FROM c AS `c`")

    def test_all_d(self):
        q = SelectMySQL(D)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c` FROM d AS `d`")

    def test_a_b_c_d_e(self):
        q = SelectMySQL(
            D,
            columns=lambda d: (
                d.C.B.A,
                d.C.B,
                d.C,
                d,
            ),
        )

        select: str = "SELECT `b_fk_a_pk_a`.pk_a AS `a_pk_a`, `b_fk_a_pk_a`.name_a AS `a_name_a`, `b_fk_a_pk_a`.data_a AS `a_data_a`, `b_fk_a_pk_a`.date_a AS `a_date_a`, `b_fk_a_pk_a`.value AS `a_value`, `c_fk_b_pk_b`.pk_b AS `b_pk_b`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `c_fk_b_pk_b`.fk_a AS `b_fk_a`, `c_fk_b_pk_b`.data AS `b_data`, `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c` FROM d AS `d`"
        joins: str = set(
            [
                "INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c",
                "INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b",
                "INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a",
            ]
        )
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.select_joins_testing(qb, select, joins)

    def select_joins_testing(self, query_builder: QueryBuilder, select_result: str, join_result: set[str]):
        extract_joins = set([x.query(DIALECT) for x in query_builder.pop_tables_and_create_joins_from_ForeignKey(query_builder.by)])

        self.assertEqual(query_builder.SELECT.compile(DIALECT).string, select_result)
        self.assertSetEqual(extract_joins, join_result)

    # def test_get_involved_table_method_consistency(self):
    #     q = SelectMySQL(
    #         D,
    #         columns=lambda d: (
    #             d.C.B.A,
    #             d.C.B,
    #             d.C,
    #             d,
    #         ),
    #     )
    #     tuple_ = set(q.tables)

    #     self.assertSetEqual(tuple_, set([A, B, C, D]))

    def test_check_private_variabels(self):
        def _lambda(d, c, b, a):
            return d, c, b, a

        q = SelectMySQL((D, C, B, A), columns=_lambda)

        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(q.table, D)
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(q._table, (D, C, B, A))

        self.assertTrue(callable(q._columns))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(q._columns, _lambda)

    def test_one_col_from_RIGHT_INCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.RIGHT_INCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` RIGHT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_LEFT_INCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.LEFT_INCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` LEFT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_RIGHT_EXCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.RIGHT_EXCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` RIGHT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_LEFT_EXCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.LEFT_EXCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` LEFT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_FULL_OUTER_INCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.FULL_OUTER_INCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` RIGHT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_FULL_OUTER_EXCLUSIVE_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.FULL_OUTER_EXCLUSIVE, dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d` RIGHT JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c")

    def test_one_col_from_INNER_JOIN_table(self):
        q = SelectMySQL(D, lambda d: d.C.data_c)
        qb = QueryBuilder(by=JoinType.INNER_JOIN, dialect=DIALECT)
        qb.add_statement(q)
        select = "SELECT `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d`"
        joins = set(["INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"])
        self.select_joins_testing(qb, select, joins)

    def test_one_column_without_fk(self):
        q = SelectMySQL(D, lambda d: (d.pk_d))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d`.pk_d AS `d_pk_d` FROM d AS `d`")

    def test_all_column_without_fk(self):
        q = SelectMySQL(D, lambda d: (d))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c` FROM d AS `d`")

    def test_two_column_with_one_fk(self):
        q = SelectMySQL(D, lambda d: (d.pk_d, d.C.data_c))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        select = "SELECT `d`.pk_d AS `d_pk_d`, `d_fk_c_pk_c`.data_c AS `c_data_c` FROM d AS `d`"
        joins = set(["INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"])
        self.select_joins_testing(qb, select, joins)

    def test_all_column_from_all_tables_with_one_fk(self):
        q = SelectMySQL(D, lambda d: (d, d.C))
        mssg: str = "SELECT `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c`, `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), mssg)

    def test_one_column_with_two_fk_in_one_table(self):
        q = SelectMySQL(D, lambda d: (d.ExtraC.data_extra_c))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), "SELECT `d_fk_extra_c_pk_extra_c`.data_extra_c AS `extra_c_data_extra_c` FROM d AS `d` INNER JOIN extra_c AS `d_fk_extra_c_pk_extra_c` ON `d`.fk_extra_c = `d_fk_extra_c_pk_extra_c`.pk_extra_c")

    def test_all_column_with_two_fk_in_one_table(self):
        q = SelectMySQL(D, lambda d: (d.ExtraC))
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        mssg: str = "SELECT `d_fk_extra_c_pk_extra_c`.pk_extra_c AS `extra_c_pk_extra_c`, `d_fk_extra_c_pk_extra_c`.data_extra_c AS `extra_c_data_extra_c` FROM d AS `d` INNER JOIN extra_c AS `d_fk_extra_c_pk_extra_c` ON `d`.fk_extra_c = `d_fk_extra_c_pk_extra_c`.pk_extra_c"
        self.assertEqual(qb.query(DIALECT), mssg)

    def test_select_with_concat(self):
        selected = SelectMySQL(
            D,
            lambda d: (
                d,
                d.C.B.A.data_a,
                d.C,
                func.Concat[D]((D.pk_d, "-", D.C.pk_c, "-", D.C.B.pk_b, "-", D.C.B.A, "-", D.C.B.data), alias_clause="concat_pks", dialect=DIALECT),
                Count(D.C.B.A.name_a, dialect=DIALECT),
                func.Max(D.C.B.A.data_a, dialect=DIALECT),
            ),
        )
        # TODOL [x]: when all errors have been fixed, implement the way to pass column name inside of Count clause to count all not NULL rows.
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(selected)
        select = "SELECT `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c`, `b_fk_a_pk_a`.data_a AS `a_data_a`, `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, CONCAT(`d`.pk_d, '-', `d_fk_c_pk_c`.pk_c, '-', `c_fk_b_pk_b`.pk_b, '-', `b_fk_a_pk_a`.pk_a, `b_fk_a_pk_a`.name_a, `b_fk_a_pk_a`.data_a, `b_fk_a_pk_a`.date_a, `b_fk_a_pk_a`.value, '-', `c_fk_b_pk_b`.data) AS `concat_pks`, COUNT(`b_fk_a_pk_a`.name_a) AS `count`, MAX(`b_fk_a_pk_a`.data_a) AS `max` FROM d AS `d`"
        joins = set(
            [
                "INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c",
                "INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b",
                "INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a",
            ]
        )
        self.select_joins_testing(qb, select, joins)

    def test_select_with_count(self):
        selected = SelectMySQL(D, columns=Count(D.C, dialect=DIALECT))
        mssg: str = "SELECT COUNT(*) AS `count` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(selected)
        self.assertEqual(qb.query(DIALECT), mssg)

    # TODOM []: Check how to deal with aliases
    def test_select_with_multiples_count(self):
        selected = SelectMySQL(
            D,
            columns=(
                Count(D.C, alias_table="c", alias_clause="COUNT~fk", dialect=DIALECT),
                Count(D, alias_table="d", alias_clause="COUNT~pk", dialect=DIALECT),
            ),
        )
        mssg: str = "SELECT COUNT(`d_fk_c_pk_c`.*) AS `COUNT~fk`, COUNT(`d`.*) AS `COUNT~pk` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"
        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(selected)
        self.assertEqual(qb.query(DIALECT), mssg)

    def test_select_with_select_inside(self) -> None:
        q = SelectMySQL(
            D,
            lambda d: (
                d.C,
                func.Concat((D.pk_d, "-", D.data_d), dialect=DIALECT),
            ),
        )

        query = "SELECT `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, CONCAT(`d`.pk_d, '-', `d`.data_d) AS `concat` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c"

        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)
        self.assertEqual(qb.query(DIALECT), query)

    def test_select_with_context(self):
        q = SelectMySQL(
            D,
            columns=(
                D.C,
                D.C.B,
                D.C.B.A,
                func.Concat((D.pk_d, "-", D.data_d), dialect=DIALECT),
            ),
        )

        qb = QueryBuilder(dialect=DIALECT)
        qb.add_statement(q)

        select = "SELECT `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, `c_fk_b_pk_b`.pk_b AS `b_pk_b`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `c_fk_b_pk_b`.fk_a AS `b_fk_a`, `c_fk_b_pk_b`.data AS `b_data`, `b_fk_a_pk_a`.pk_a AS `a_pk_a`, `b_fk_a_pk_a`.name_a AS `a_name_a`, `b_fk_a_pk_a`.data_a AS `a_data_a`, `b_fk_a_pk_a`.date_a AS `a_date_a`, `b_fk_a_pk_a`.value AS `a_value`, CONCAT(`d`.pk_d, '-', `d`.data_d) AS `concat` FROM d AS `d`"
        joins = set(
            [
                "INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c",
                "INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b",
                "INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a",
            ]
        )
        self.select_joins_testing(qb, select, joins)


if "__main__" == __name__:
    unittest.main()
