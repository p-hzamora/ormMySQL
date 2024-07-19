# Standard libraries
# Third party libraries
import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


# Custom libraries
from orm import MySQLRepository  # noqa: E402


TDDBB_name = "__test_ddbb__"
TTABLE_name = "__test_table__"

data_config = {"user": "root", "password": "1234"}


class Test_my_sql(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb = MySQLRepository(**data_config).connect()
        self.ddbb.create_database(TDDBB_name, "replace")

    def tearDown(self) -> None:
        self.ddbb.drop_database(TDDBB_name)

    def test_create_table_code_first_passing_folder(self):
        self.ddbb.create_tables_code_first("test/models")

    def test_create_table_code_first_passing_file(self):
        self.ddbb.create_tables_code_first("test/models/models_in_the_same_file/all_models_in_one_file.py")
        pass


if __name__ == "__main__":
    unittest.main()
