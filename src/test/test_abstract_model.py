import unittest


from test.config import config_dict
from test.models import (  # noqa: E402
    City,
    Country,
)

from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda.databases.my_sql import MySQLStatements  # noqa: E402

db = MySQLRepository(**config_dict)


class TestAbstractSQLStatements(unittest.TestCase):
    def test_constructor(self):
        city = MySQLStatements[City](City, db)
        country = MySQLStatements[Country](Country, db)

        rusult_ci = city.select(flavour=set)
        result_co = country.select(flavour=set)

        self.assertIsInstance(rusult_ci, tuple)
        self.assertIsInstance(rusult_ci[0], set)

        self.assertIsInstance(result_co, tuple)
        self.assertIsInstance(result_co[0], set)


if __name__ == "__main__":
    unittest.main()
