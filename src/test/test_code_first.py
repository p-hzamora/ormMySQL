# Standard libraries
# Third party libraries
import unittest
import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


# Custom libraries
from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from test.models import Country  # noqa: E402
from ormlambda import ORM

DB_NAME = "__test_ddbb__"


class Test_my_sql(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ddbb = create_env_engine()
        cls.ddbb.create_database(DB_NAME, "replace")

        cls.engine = create_engine_for_db(DB_NAME)
        cls.country_model = ORM(Country, cls.engine)


    def tearDown(self) -> None:
        self.ddbb.drop_database(DB_NAME)

    # FIXME [ ]: refactor to fix and include this method
    def test_create_table_code_first_passing_folder(self):
        self.ddbb.create_tables_code_first("src/test/models")

    # FIXME [ ]: refactor to fix and include this method
    def test_create_table_code_first_passing_file(self):
        return
        self.ddbb.create_tables_code_first("src/test/models/models_in_the_same_file/all_models_in_one_file.py")
        pass

    def test_create_table(self):
        if self.country_model.table_exists():
            self.ddbb.drop_table(Country.__table_name__)
        self.country_model.create_table()


if __name__ == "__main__":
    unittest.main()
