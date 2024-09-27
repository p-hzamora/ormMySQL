import unittest
import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql.clauses import (  # noqa: E402
    JoinSelector,
    JoinType,
)
from models import City, Country, Address  # noqa: E402
# from models.address import Address


class TestJoinSelector(unittest.TestCase):
    def test_constructor(self):
        join_selector = JoinSelector[Address, City](
            table_left=Address,
            table_right=City,
            by=JoinType.INNER_JOIN,
            where=lambda a, c: a.city_id == c.city_id,
        )

        self.assertEqual(
            join_selector.query,
            "INNER JOIN city ON address.city_id = city.city_id",
        )

    def test_inner_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            where=lambda x: x.country_id == x.country_id,
            by=JoinType.INNER_JOIN,
        )

        query_parser = qs.query
        query = "INNER JOIN country ON city.country_id = country.country_id"
        self.assertEqual(query, query_parser)

    def test_right_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            col_left="country_id",
            col_right="country_id",
            by=JoinType.RIGHT_EXCLUSIVE,
        )

        query_parser = qs.query
        query = "RIGHT JOIN country ON city.country_id = country.country_id"

        self.assertEqual(query, query_parser)

    def test_left_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda ci, co: ci.country_id == co.country_id,
        )

        query_parser = qs.query
        query = "LEFT JOIN country ON city.country_id = country.country_id"
        self.assertEqual(query, query_parser)

    def test_join_selectors(self):
        s1 = JoinSelector[Address, City](
            table_left=Address,
            table_right=City,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda a, c: a.city_id == c.city_id,
        )

        s2 = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda ci, co: ci.country_id == co.country_id,
        )
        query_parser = JoinSelector.join_selectors(s1, s2)
        query = "LEFT JOIN city ON address.city_id = city.city_id\nLEFT JOIN country ON city.country_id = country.country_id"
        self.assertEqual(query, query_parser)

    def test__eq__method(self):
        s1 = JoinSelector[Address, City](
            table_left=Address,
            table_right=City,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda a, c: a.city_id == c.city_id,
        )
        s2 = JoinSelector[Address, City](
            table_left=Address,
            table_right=City,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda a, c: a.city_id == c.city_id,
        )

        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
