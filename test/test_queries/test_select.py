import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.queries.select import SelectQuery  # noqa: E402
from test.models import (  # noqa: E402
    City,
    Address,
    Country,
)


class TestQuery(unittest.TestCase):
    def test_select_all_col_with_no_select_list_attr(self):
        q = SelectQuery[City](City)
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City, select_lambda=lambda: "*")
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_one_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: c.city)
        self.assertEqual(q.query, "SELECT city.city FROM city")

    def test_select_two_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city.city, city.city_id FROM city")

    def test_select_three_col(self):
        q = SelectQuery[City](City, select_lambda=lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city.city, city.last_update, city.country_id FROM city")

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
        self.assertEqual(q.query, "SELECT address.*, city.*, country.*, city.country_id, address.city_id, address.last_update, country.country FROM address")

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
        self.assertEqual(q.query, "SELECT address.*, city.*, country.* FROM address")

    def test_select_all_columns_from_tables_without_use_all_vars(self):
        # this response must not be the real one,
        q = SelectQuery[Address, City, Country](
            Address,
            City,
            select_lambda=lambda a, ci: (
                a,
                ci.country,
            ),
        )
        self.assertEqual(q.query, "SELECT address.*, country.* FROM address")


if "__main__" == __name__:
    unittest.main()
