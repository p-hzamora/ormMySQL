import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.foreign_key import ForeignKey
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql.clauses import (  # noqa: E402
    JoinSelector,
    JoinType,
)
from test.models import City, Country, Address  # noqa: E402
# from test.models.address import Address


class TestJoinSelector(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        ForeignKey.clear()

        return None

    def test_constructor(self):
        join_selector = JoinSelector[Address, City](
            where=Address.city_id == City.city_id,
            by=JoinType.INNER_JOIN,
        )

        self.assertEqual(
            join_selector.query,
            "INNER JOIN city AS `city` ON address.city_id = `city`.city_id",
        )

    def test_inner_join(self):
        join = JoinSelector[City, Country](
            where=City.country_id == Country.country_id,
            by=JoinType.INNER_JOIN,
        )

        query_parser = join.query
        query = "INNER JOIN country AS `country` ON city.country_id = `country`.country_id"
        self.assertEqual(query, query_parser)

    # def test_right_join(self):
    #     join = JoinSelector[City, Country](
    #         table_left=City,
    #         table_right=Country,
    #         col_left="country_id",
    #         col_right="country_id",
    #         by=JoinType.RIGHT_EXCLUSIVE,
    #     )

    # query_parser = join.query
    # query = "RIGHT JOIN country ON `city`.country_id = `country`.country_id"

    # self.assertEqual(query, query_parser)

    def test_left_join(self):
        join = JoinSelector[City, Country](
            by=JoinType.LEFT_EXCLUSIVE,
            where=City.country_id == Country.country_id,
        )

        query_parser = join.query
        query = "LEFT JOIN country AS `country` ON city.country_id = `country`.country_id"
        self.assertEqual(query, query_parser)

    def test_join_selectors(self):
        ctx = ClauseInfoContext()

        s1 = JoinSelector[Address, City](
            by=JoinType.LEFT_EXCLUSIVE,
            where=Address.city_id == City.city_id,
            context=ctx,
        )

        s2 = JoinSelector[City, Country](
            by=JoinType.LEFT_EXCLUSIVE,
            where=City.country_id == Country.country_id,
            context=ctx,
        )
        query_parser = JoinSelector.join_selectors(s1, s2)
        query = "LEFT JOIN city AS `city` ON address.city_id = `city`.city_id\nLEFT JOIN country AS `country` ON `city`.country_id = `country`.country_id"
        self.assertEqual(query, query_parser)

    def test__eq__method(self):
        s1 = JoinSelector[Address, City](
            by=JoinType.LEFT_EXCLUSIVE,
            where=Address.city_id == City.city_id,
        )
        s2 = JoinSelector[Address, City](
            by=JoinType.LEFT_EXCLUSIVE,
            where=Address.city_id == City.city_id,
        )

        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
