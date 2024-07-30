import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from test.models import (  # noqa: E402
    City,
    Address,
    Country,
)


from orm.databases.my_sql.repository import MySQLRepository  # noqa: E402
from orm.databases.my_sql.statements import MySQLStatements  # noqa: E402
from orm.abstract_model import AbstractSQLStatements

config = {"user": "root", "password": "1234", "database": "sakila"}
db = MySQLRepository(**config)


class TestAbstractSQLStatements(unittest.TestCase):
    def test_constructor(self):
        abstract = MySQLStatements[Address](Address, db)
        address = abstract.select()
        pass


if __name__ == "__main__":
    unittest.main()
