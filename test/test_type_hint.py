import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import unittest

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from orm import MySQLRepository, IRepositoryBase  # noqa: E402
from test.models.address import AddressModel  # noqa: E402
from test.models import Address, City, Country  # noqa: E402


load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")


database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()


a_model = AddressModel(database)


class TestTypeHint(unittest.TestCase):
    def test_SELECT_method_passing_3_columns(self):
        response = a_model.select(lambda a: (a, a.city, a.city.country))
        a, city, country = response
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(a[0], Address)
        self.assertIsInstance(city[0], City)
        self.assertIsInstance(country[0], Country)

    def test_SELECT_method_passing_1_column(self):
        response = a_model.select(lambda a: (a.city,))
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0][0], City)

    def test_SELECT_ONE_method_passing_3_columns(self):
        response = a_model.select_one(
            lambda a: (
                a,
                a.city,
                a.city.country,
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
