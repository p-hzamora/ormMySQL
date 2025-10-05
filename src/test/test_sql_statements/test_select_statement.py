import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_sakila_engine  # noqa: E402
from ormlambda.dialects import mysql
from test.models import Address, City, Country
from ormlambda import ORM

DIALECT = mysql.dialect


engine = create_sakila_engine()


class TestSelectTest(unittest.TestCase):
    def test_select_all(self):
        model = ORM(Address, engine)

        res1 = model.select()
        res2 = model.select(lambda x: x)
        res3 = model.select(lambda x: (x,))

        self.assertIsInstance(res1, tuple)
        self.assertIsInstance(res1[0], Address)
        self.assertEqual(res1, res2)
        self.assertEqual(res2, res3)

    def test_select_all_different_tables(self):
        model = ORM(Address, engine)

        res1 = model.select(
            lambda x: (
                x,
                x.City,
                x.City.Country,
            ),
            avoid_duplicates=True,
        )

        self.assertIsInstance(res1, tuple)
        self.assertIsInstance(res1[0][0], Address)
        self.assertIsInstance(res1[0][1], City)
        self.assertIsInstance(res1[0][2], Country)

        for a, ci, co in res1:
            self.assertEqual(a.city_id, ci.city_id)
            self.assertEqual(ci.country_id, co.country_id)


if __name__ == "__main__":
    unittest.main(failfast=True)
