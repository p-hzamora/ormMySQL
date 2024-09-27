import unittest
import sys
from pathlib import Path
from config import config_dict

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.test.models import (  # noqa: E402
    City,
    Country,
)

from src.ormlambda.databases.my_sql.repository import MySQLRepository  # noqa: E402
from src.ormlambda.databases.my_sql.statements import MySQLStatements  # noqa: E402

db = MySQLRepository(**config_dict)
db.set_config({"database": "sakila"})


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
