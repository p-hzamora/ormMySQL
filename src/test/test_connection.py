import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())
from ormlambda import create_engine


class TestTypeHint(unittest.TestCase):
    def test_connection_default(self):
        engine = create_engine("mysql://root:1500@localhost:3306?")

        self.assertEqual(repr(engine), "Engine: mysql://root:***@localhost:3306")

        self.assertEqual(engine.repository.pool.pool_size, 5)
        self.assertEqual(engine.repository.database, None)

    def test_connection_(self):
        engine = create_engine("mysql://root:1500@localhost:3306/sakila?pool_size=20")

        self.assertEqual(repr(engine), "Engine: mysql://root:***@localhost:3306/sakila?pool_size=20")

        self.assertEqual(engine.repository.pool.pool_size, 20)
        self.assertEqual(engine.repository.database, "sakila")


if __name__ == "__main__":
    unittest.main()
