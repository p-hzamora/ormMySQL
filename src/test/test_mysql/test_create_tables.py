import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_engine_for_db
from test.models import City

from ormlambda import ORM

engine = create_engine_for_db("sakila")


class TestCreateMySQLTables(unittest.TestCase):
    def test_create_table(self):
        ORM(City, engine).create_table("append")


if __name__ == "__main__":
    unittest.main()
