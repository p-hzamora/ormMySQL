import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import ORM
from test.models import Address, City, Country  # noqa: E402


from test.env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)

db = MySQLRepository(user=DB_USERNAME, password=DB_PASSWORD, database=DB_DATABASE, host=DB_HOST)

AddressModel = ORM(Address, db)
CountryModel = ORM(Country, db)
CityModel = ORM(City, db)


class TestMax(unittest.TestCase):
    def test_max_using_select_one(self):
        max = AddressModel.select_one(AddressModel.max(Address.address_id), flavour=dict)["max"]
        self.assertEqual(max, 605)

    def test_max_using_max(self):
        max = AddressModel.max(Address.address_id, execute=True)
        self.assertEqual(max, 605)

    def test_max_using_where_condition(self):
        MAX_VALUE = 300
        result = AddressModel.where(lambda x: x.address_id <= MAX_VALUE).max(Address.address_id, execute=True)
        self.assertEqual(result, MAX_VALUE)


if __name__ == "__main__":
    unittest.main()
