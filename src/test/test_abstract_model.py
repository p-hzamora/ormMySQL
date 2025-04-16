import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_engine_for_db
from test.models import (  # noqa: E402
    City,
    Country,
)

from ormlambda.databases.my_sql import MySQLStatements  # noqa: E402

engine = create_engine_for_db('sakila')

class TestAbstractSQLStatements(unittest.TestCase):
    def test_constructor(self):
        city = MySQLStatements[City](City, engine)
        country = MySQLStatements[Country](Country, engine)

        rusult_ci = city.select(flavour=set)
        result_co = country.select(flavour=set)

        self.assertIsInstance(rusult_ci, tuple)
        self.assertIsInstance(rusult_ci[0], set)

        self.assertIsInstance(result_co, tuple)
        self.assertIsInstance(result_co[0], set)


if __name__ == "__main__":
    unittest.main()
