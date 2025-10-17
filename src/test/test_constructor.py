import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import config_dict
from test.config import create_sakila_engine  # noqa: E402


class TestTypeHint(unittest.TestCase):
    def test_initialize_MySQLRepository_with_kwargs(self) -> None:
        engine = create_sakila_engine()

        ddbb = engine.repository

        self.assertEqual(ddbb.database, config_dict["database"])
        self.assertEqual(ddbb.database, config_dict["database"])

        self.assertEqual(ddbb._pool._cnx_config["user"], config_dict["user"])
        self.assertEqual(ddbb._pool._cnx_config["password"], config_dict["password"])
        self.assertEqual(ddbb._pool._cnx_config["host"], config_dict["host"])



if __name__ == "__main__":
    unittest.main()
