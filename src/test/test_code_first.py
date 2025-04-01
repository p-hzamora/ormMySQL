# Standard libraries
# Third party libraries
import unittest
import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


# Custom libraries
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from config import config_dict  # noqa: E402

from test.models import Country, CountryModel  # noqa: E402

TDDBB_name = "__test_ddbb__"


class Test_my_sql(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb = MySQLRepository(**config_dict)
        if self.ddbb.database_exists(TDDBB_name):
            self.ddbb.drop_database(TDDBB_name)
        self.ddbb.create_database(TDDBB_name, "replace")
        self.ddbb.database = TDDBB_name

    def tearDown(self) -> None:
        self.ddbb.drop_database(TDDBB_name)

    def test_create_table_code_first_passing_folder(self):
        self.ddbb.create_tables_code_first("src/test/models")

    def test_create_table_code_first_passing_file(self):
        return
        self.ddbb.create_tables_code_first("src/test/models/models_in_the_same_file/all_models_in_one_file.py")
        pass

    def test_create_table(self):
        if CountryModel(self.ddbb).table_exists():
            self.ddbb.drop_table(Country.__table_name__)
        CountryModel(self.ddbb).create_table()


if __name__ == "__main__":
    unittest.main()
