import sys
from pathlib import Path
from decouple import config
import unittest

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from src.databases.my_sql import MySQLRepository  # noqa: E402
from src.common.interfaces import IRepositoryBase  # noqa: E402
from test.models.address import AddressModel  # noqa: E402
from test.models import Address, City, Country  # noqa: E402


USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
HOST = config("HOST")


database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST)


a_model = AddressModel(database)


class TestTypeHint(unittest.TestCase):
    def test_SELECT_method_passing_3_columns(self):
        response = a_model.select(lambda a: (a, a.City, a.City.Country))
        a, city, country = response
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(a[0], Address)
        self.assertIsInstance(city[0], City)
        self.assertIsInstance(country[0], Country)

    def test_SELECT_method_passing_1_column(self):
        response = a_model.select(lambda a: (a.City,))
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0][0], City)

    def test_SELECT_ONE_method_passing_0_column(self):
        response = a_model.select_one()
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_tuple_with_table_itself(self):
        response = a_model.select_one(lambda x: (x,))
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_the_same_table_itself(self):
        response = a_model.select_one(lambda x: x)
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_3_columns_of_the_same_table(self):
        response = a_model.select_one(lambda x: (x.address, x.address2, x.city_id), flavour=tuple)
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0], str)
        self.assertIsInstance(response[1], str)
        self.assertIsInstance(response[2], int)

    def test_SELECT_ONE_method_passing_3_columns(self):
        response = a_model.select_one(
            lambda a: (
                a,
                a.City,
                a.City.Country,
            )
        )
        a, city, country = response
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(a, Address)
        self.assertIsInstance(city, City)
        self.assertIsInstance(country, Country)

    def test_SELECT_ONE_method_passing_1_column(self):
        response = a_model.select_one(lambda a: (a,))

        self.assertIsInstance(response, Address)
        self.assertIsInstance(response.address, str)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_DICT(self):
        response = a_model.select_one(lambda a: (a,), flavour=dict)
        self.assertIsInstance(response, dict)
        self.assertIsInstance(list(response.values())[0], int)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_TUPLE(self):
        response = a_model.select_one(lambda a: (a,), flavour=tuple)
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0], int)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_LIST(self):
        response = a_model.select_one(lambda a: (a,), flavour=list)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0], int)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_SET(self):
        response = a_model.select_one(lambda a: (a,), flavour=set)
        self.assertIsInstance(response, set)
        self.assertEqual("Alberta" in response, True)


if __name__ == "__main__":
    unittest.main()
