import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.queries.select import SelectQuery  # noqa: E402
from test.models import City, Address  # noqa: E402


class TestQuery(unittest.TestCase):
    def test_select_all_col_with_no_select_list_attr(self):
        q = SelectQuery[City](City)
        self.assertEqual(q.query, "SELECT * FROM city")
        self.assertEqual(q.load(), "SELECT * FROM city;")

    def test_select_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City,lambda: "*")
        self.assertEqual(q.query, "SELECT * FROM city")
        self.assertEqual(q.load(), "SELECT * FROM city;")

    def test_select_one_col(self):
        q = SelectQuery[City](City, lambda c: c.city)
        self.assertEqual(q.query, "SELECT city FROM city")
        self.assertEqual(q.load(), "SELECT city FROM city;")

    def test_select_two_col(self):
        q = SelectQuery[City](City, lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city, city_id FROM city")
        self.assertEqual(q.load(), "SELECT city, city_id FROM city;")

    def test_select_three_col(self):
        q = SelectQuery[City](City, lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city, last_update, country_id FROM city")
        self.assertEqual(q.load(), "SELECT city, last_update, country_id FROM city;")

    def test_select_cols_from_foreign_keys(self):
        q = SelectQuery[Address](City, lambda a: (a.city.city_id))
        self.assertEqual(q.query, "SELECT city.city_id, last_update, country_id FROM city")


if "__main__" == __name__:
    unittest.main()
