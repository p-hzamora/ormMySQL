import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import config_dict
from test.config import create_sakila_engine  # noqa: E402
from test.models import CountryModel  # noqa: E402


class TestTypeHint(unittest.TestCase):
    def test_initialize_MySQLRepository_with_kwargs(self) -> None:
        engine = create_sakila_engine()

        ddbb = engine.repository

        self.assertEqual(ddbb.database, config_dict["database"])
        self.assertEqual(ddbb.database, config_dict["database"])

        self.assertEqual(ddbb._pool._cnx_config["user"], config_dict["user"])
        self.assertEqual(ddbb._pool._cnx_config["password"], config_dict["password"])
        self.assertEqual(ddbb._pool._cnx_config["host"], config_dict["host"])

    def test_raise_ValueError_if_Model_has_not_get_IRepositoryModel(self) -> None:
        with self.assertRaises(ValueError):
            try:
                CountryModel(None)
            except ValueError as err:
                mssg: str = "`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class"
                self.assertEqual(mssg, err.args[0])
                raise ValueError


if __name__ == "__main__":
    unittest.main()
