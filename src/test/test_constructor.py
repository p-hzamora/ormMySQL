import sys
from pathlib import Path
import unittest
from config import config_dict

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda.common.interfaces import IRepositoryBase  # noqa: E402
from models import CountryModel  # noqa: E402


class TestTypeHint(unittest.TestCase):
    def test_initialize_MySQLRepository_with_kwargs(self) -> None:
        ddbb: IRepositoryBase = MySQLRepository(**config_dict)

        ddbb.connect()
        self.assertEqual(ddbb.database, config_dict["database"])
        self.assertEqual(ddbb.connection.database, config_dict["database"])

        self.assertEqual(ddbb.connection.user, config_dict["user"])
        self.assertEqual(ddbb.connection._password, config_dict["password"])
        self.assertEqual(ddbb.connection._host, config_dict["host"])

    def test_raise_ValueError_if_Model_has_not_get_IRepositoryModel(self) -> None:
        ddbb: IRepositoryBase = MySQLRepository(**config_dict).connect()

        with self.assertRaises(ValueError):
            try:
                CountryModel(ddbb)
            except ValueError as err:
                mssg: str = "`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class"
                self.assertEqual(mssg, err.args[0])
                raise ValueError


if __name__ == "__main__":
    unittest.main()
