import unittest
import sys
from pathlib import Path
import random

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from config import config_dict
from ormlambda import Table, BaseModel, IRepositoryBase, Column
from ormlambda.databases.my_sql import MySQLRepository

DATABASE_NAME = "__ddbb_test__"


class TableCount(Table):
    __table_name__ = "table_count"
    pos: int = Column[int](is_primary_key=True)
    a: int
    b: int
    c: int


class TableCountModel(BaseModel[TableCount]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, TableCount, repository)


class CountTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb = MySQLRepository(**config_dict)

        self.ddbb.create_database(DATABASE_NAME, "replace")
        self.ddbb.database = DATABASE_NAME

        self.model = TableCountModel(self.ddbb)

        TableCountModel(self.ddbb).create_table()

    def tearDown(self) -> None:
        self.ddbb.drop_database(DATABASE_NAME)

    def TableCount_generator(self, n: int) -> None:
        if not n > 0:
            raise ValueError(f"'n' must not be less than '0'. You passed '{n}'")

        insert_values = []
        for x in range(0, n):
            rnd = lambda: random.randint(0, 1_000_000)  # noqa: E731
            insert_values.append(TableCount(x, rnd(), rnd(), rnd()))
        return insert_values

    def test_count_all_rows(self):
        n_before_insert = self.model.count()

        self.model.insert(self.TableCount_generator(4))
        n_after_insert = self.model.count()

        self.model.delete()
        n_after_delete = self.model.count()

        self.assertEqual(n_before_insert, 0)
        self.assertEqual(n_after_insert, 4)
        self.assertEqual(n_after_delete, n_before_insert)

    def test_count_when_filtering(self):
        self.model.insert(self.TableCount_generator(100))

        n_select = self.model.where(lambda x: 50 <= x.pos <= 70).count()

        self.assertEqual(n_select, 21)

    def test_clean_query_list(self):
        n = self.model.where(lambda x: x.a == 10).count()

        self.assertEqual(n, 0)
        self.assertEqual(self.model._query_list, {})


if __name__ == "__main__":
    unittest.main()
