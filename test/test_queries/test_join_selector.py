import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from orm.orm_objects.queries import (
    JoinSelector,
    JoinType,
)
from models.city import City
from models.country import Country
# from models.address import Address


class TestJoinSelector(unittest.TestCase):
    def test_inner_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            where=lambda x: x.country_id == x.country_id,
            by=JoinType.INNER_JOIN,
        )

        query_parser = qs.load()
        query = "INNER JOIN country ON city.country_id = country.country_id;"
        self.assertEqual(query, query_parser)

    def test_right_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            col_left="country_id",
            col_right="country_id",
            by=JoinType.RIGHT_EXCLUSIVE,
        )

        query_parser = qs.load()
        query = "RIGHT JOIN country ON city.country_id = country.country_id;"

        self.assertEqual(query, query_parser)

    def test_left_join(self):
        qs = JoinSelector[City, Country](
            table_left=City,
            table_right=Country,
            by=JoinType.LEFT_EXCLUSIVE,
            where=lambda x: x.country_id == x.country_id,
        )

        query_parser = qs.load()
        query = "LEFT JOIN country ON city.country_id = country.country_id;"
        self.assertEqual(query, query_parser)


if __name__ == "__main__":
    unittest.main()
