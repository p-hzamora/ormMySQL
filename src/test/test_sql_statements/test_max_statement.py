import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM, Max
from test.models import Address, City, Country  # noqa: E402
from test.config import create_sakila_engine


db = create_sakila_engine()

AddressModel = ORM(Address, db)
CountryModel = ORM(Country, db)
CityModel = ORM(City, db)


class TestMax(unittest.TestCase):
    def test_max_using_select_one(self):
        max = AddressModel.select_one(lambda x: Max(x.address_id), flavour=dict)["max"]
        self.assertEqual(max, 605)

    def test_max_using_max(self):
        max = AddressModel.max(lambda x: x.address_id)
        self.assertEqual(max, 605)

    def test_max_using_where_condition(self):
        MAX_VALUE = 300
        result = AddressModel.where(lambda x: x.address_id <= MAX_VALUE).max(lambda x: x.address_id)
        self.assertEqual(result, MAX_VALUE)


if __name__ == "__main__":
    unittest.main()
