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


if __name__ == "__main__":
    # cond = 2
    # select = SelectQuery[City](City, where=lambda x: x.city_id >= cond).query

    innerjoin = JoinSelector[City, Country](
        table_left=City,
        table_right=Country,
        by=JoinType.INNER_JOIN,
        select_list=lambda c: [c.city_id, c.last_update, c.country],
        where=lambda c, x: c.country_id == x.country_id,
    )
    query = innerjoin.load()

    unittest.main()
