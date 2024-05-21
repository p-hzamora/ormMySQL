import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from orm.orm_objects.queries import (
    SelectQuery,
    JoinSelector,
    JoinType,
    WhereCondition,
)
from models.city import City
from models.country import Country
from models.address import Address


class TestQuerySelector(unittest.TestCase):
    def test_query_all_names(self):
        qs = SelectQuery[Country](Country)
        self.assertEqual(qs.load(), "SELECT * FROM country;")

    def test_query_select_names_callable(self):
        qs = SelectQuery[City](City, select_list=lambda x: x.last_update)
        self.assertEqual(qs.load(), "SELECT last_update FROM city;")

    def test_query_select_names_iterable_callable(self):
        qs = SelectQuery[City](City, select_list=[lambda x: x.city, lambda x: x.country_id, lambda x: x.city_id])
        self.assertEqual(qs.load(), "SELECT city, country_id, city_id FROM city;")


class TestJoinSelector(unittest.TestCase):
    def test_inner_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            col_left=lambda x: x.country_id,
            col_right=lambda x: x.country_id,
            by=JoinType.INNER_JOIN,
        )

        query_parser = qs.load()
        query = "SELECT * FROM city INNER JOIN country ON city.country_id = country.country_id;"
        self.assertEqual(query, query_parser)

    def test_right_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            col_left=lambda x: x.country_id,
            table_right=Country,
            col_right=lambda x: x.country_id,
            by=JoinType.RIGHT_EXCLUSIVE,
        )

        query_parser = qs.load()
        query = "SELECT * FROM city RIGHT JOIN country ON city.country_id = country.country_id;"

        self.assertEqual(query, query_parser)

    def test_left_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            col_left=lambda x: x.country_id,
            table_right=Country,
            col_right=lambda x: x.country_id,
            by=JoinType.LEFT_EXCLUSIVE,
        )

        query_parser = qs.load()
        query = "SELECT * FROM city LEFT JOIN country ON city.country_id = country.country_id;"
        self.assertEqual(query, query_parser)


class C:
    c: str
    data: str


class B:
    b: str
    c: C
    value: None


class A:
    a: str
    b: B


class TestCondition(unittest.TestCase):
    COND_1 = WhereCondition[City, Country](lambda x, y: x.last_update != y.country_id)
    COND_2 = WhereCondition[Address, City](lambda a, c: a.address2 <= c.city_id)
    COND_3 = WhereCondition[A, B](lambda a, b: a.b.value == b.c.data)

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_1, WhereCondition)
        self.assertIsInstance(self.COND_2, WhereCondition)
        self.assertIsInstance(self.COND_3, WhereCondition)

    def test_to_query_cond_1(self):
        self.assertEqual(self.COND_1.to_query(), "WHERE last_update != country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(self.COND_2.to_query(), "WHERE address2 <= city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(self.COND_3.to_query(), "WHERE value = data")

    def test_join_condition_restrictive_false(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=False)
        self.assertEqual(joins, "WHERE (last_update != country_id) OR (address2 <= city_id) OR (value = data)")

    def test_join_condition_restrictive_true(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=True)
        self.assertEqual(joins, "WHERE (last_update != country_id) AND (address2 <= city_id) AND (value = data)")


if __name__ == "__main__":
    # cond = 2
    # select = SelectQuery[City](City, where=lambda x: x.city_id >= cond).query

    innerjoin = JoinSelector[City, Country](
        table_left=City,
        table_right=Country,
        col_left=lambda c: c.country_id,
        col_right=lambda c: c.country_id,
        by=JoinType.INNER_JOIN,
        select_list=lambda c: [c.city_id, c.last_update, c.country],
        where=lambda c, x: c.country_id == x.country_id,
    )
    query = innerjoin.load()

    unittest.main()
