import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.queries.select import SelectQuery  # noqa: E402
from test.models import (  # noqa: E402
    City,
    CityModel,
    Address,
    AddressModel,
    Actor,
    ActorModel,
    Country,
    CountryModel,
)
from orm import Table



class TestQuery(unittest.TestCase):
    def test_select_all_col_with_no_select_list_attr(self):
        q = SelectQuery[City](City)
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_all_col_with_select_list_attr(self):
        q = SelectQuery[City](City, lambda: "*")
        self.assertEqual(q.query, "SELECT * FROM city")

    def test_select_one_col(self):
        q = SelectQuery[City](City, lambda c: c.city)
        self.assertEqual(q.query, "SELECT city FROM city")

    def test_select_two_col(self):
        q = SelectQuery[City](City, lambda c: (c.city, c.city_id))
        self.assertEqual(q.query, "SELECT city, city_id FROM city")

    def test_select_three_col(self):
        q = SelectQuery[City](City, lambda c: (c.city, c.last_update, c.country_id))
        self.assertEqual(q.query, "SELECT city, last_update, country_id FROM city")

    def test_select_cols_from_foreign_keys(self):
        # this response must not be the real one,
        a = SelectQuery(Address, City, Country, lambda a, ci, co: (a.address, ci.city_id, co.last_update))

        pass

        address = Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid")
        q = SelectQuery[Address](address, lambda a: (a.city.country.country))
        self.assertEqual(q.query, "SELECT city.city_id, address.last_update, address.country_id FROM address")


if "__main__" == __name__:
    unittest.main()
