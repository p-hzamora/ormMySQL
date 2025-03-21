import unittest
import sys
from pathlib import Path
import random


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from config import config_dict
from ormlambda import Table, BaseModel, BaseRepository, Column
from ormlambda.databases.my_sql import MySQLRepository

DATABASE_NAME = "__ddbb_test__"


class TableCount(Table):
    __table_name__ = "table_count"
    pos: int = Column(int, is_primary_key=True)
    a: int
    b: int
    c: int


class TableCountModel(BaseModel[TableCount]):
    def __new__[TRepo](cls, repository: BaseRepository[TRepo]):
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

    def TableCount_generator(self, n: int) -> list[TableCount]:
        if not n > 0:
            raise ValueError(f"'n' must not be less than '0'. You passed '{n}'")

        insert_values: list[TableCount] = []
        for x in range(0, n):
            rnd = lambda: random.randint(0, 1_000_000)  # noqa: E731
            insert_values.append(TableCount(x, rnd(), rnd(), rnd()))
        return insert_values

    def test_count_all_rows(self):
        n_before_insert = self.model.count(execute=True)

        self.model.insert(self.TableCount_generator(4))
        n_after_insert = self.model.count(execute=True)

        self.model.delete()
        n_after_delete = self.model.count(execute=True)

        self.assertEqual(n_before_insert, 0)
        self.assertEqual(n_after_insert, 4)
        self.assertEqual(n_after_delete, n_before_insert)

    def test_count_when_filtering(self):
        self.model.insert(self.TableCount_generator(100))

        n_select = self.model.where((TableCount.pos <= 70) & (TableCount.pos >= 50)).count(execute=True)

        self.assertEqual(n_select, 21)

    def test_count_when_filtering_using_list(self):
        self.model.insert(self.TableCount_generator(100))

        n_select = self.model.where(
            [
                TableCount.pos <= 70,
                TableCount.pos >= 50,
            ]
        ).count(execute=True)

        self.assertEqual(n_select, 21)

    def test_count_excluding_NULL_for_column(self):
        all_rows = self.TableCount_generator(100)

        for x in range(100):
            if x < 10:
                all_rows[x].a = None

        self.model.insert(all_rows)

        rows_different_none = self.model.count(TableCount.a, execute=True)

        self.assertEqual(rows_different_none, 90)

    def test_clean_query_list(self):
        insert: list[TableCount] = []

        for x in range(1, 101):
            if x < 21:
                table_count: TableCount = TableCount(x, 20, x, x)
            elif 21 <= x < 81:
                table_count: TableCount = TableCount(x, 80, x, x)
            elif 81 <= x < 101:
                table_count: TableCount = TableCount(x, 100, x, x)

            insert.append(table_count)

        self.model.insert(insert)
        n = self.model.count(execute=True)
        n_20 = self.model.where(TableCount.a == 20).count(execute=True)
        n_80 = self.model.where(TableCount.a == 80).count(execute=True)
        n_100 = self.model.where(TableCount.a == 100).count(execute=True)

        self.assertEqual(n, 100)
        self.assertEqual(n_20, 20)
        self.assertEqual(n_80, 60)
        self.assertEqual(n_100, 20)

        self.assertEqual(self.model._query_builder._query_list, {})


if __name__ == "__main__":
    unittest.main()
