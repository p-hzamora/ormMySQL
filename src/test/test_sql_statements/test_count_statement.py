import unittest
import sys
from pathlib import Path
import random


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_env_engine, create_engine
from test.config import DB_PASSWORD, DB_USERNAME
from ormlambda import Table, Column, ORM

DATABASE_NAME = "__ddbb_test__"


class TableCount(Table):
    __table_name__ = "table_count"
    pos: int = Column(int, is_primary_key=True)
    a: int
    b: int
    c: int


class CountTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_env_engine()

        self.engine.create_schema(DATABASE_NAME, "replace")

        new_engine = create_engine(f"mysql://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/{DATABASE_NAME}?pool_size=3")
        self.engine = new_engine
        self.model = ORM(TableCount, self.engine)

        self.model.create_table()

    def tearDown(self) -> None:
        self.engine.drop_schema(DATABASE_NAME)

    def TableCount_generator(self, n: int) -> list[TableCount]:
        if not n > 0:
            raise ValueError(f"'n' must not be less than '0'. You passed '{n}'")

        insert_values: list[TableCount] = []
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

    def test_AAcount_when_filtering(self):
        self.model.insert(self.TableCount_generator(100))

        n_select = self.model.where(lambda x: (x.pos <= 70) & (x.pos >= 50)).count()

        self.assertEqual(n_select, 21)

    def test_count_when_filtering_using_list(self):
        self.model.insert(self.TableCount_generator(100))

        n_select = self.model.where(
            lambda x: [
                x.pos <= 70,
                x.pos >= 50,
            ]
        ).count()

        self.assertEqual(n_select, 21)

    def test_count_excluding_NULL_for_column(self):
        all_rows = self.TableCount_generator(100)

        for x in range(100):
            if x < 10:
                all_rows[x].a = None

        self.model.insert(all_rows)

        rows_different_none = self.model.count(lambda x: x.a)

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
        n = self.model.count()
        n_20 = self.model.where(lambda x: x.a == 20).count()
        n_80 = self.model.where(lambda x: x.a == 80).count()
        n_100 = self.model.where(lambda x: x.a == 100).count()

        self.assertEqual(n, 100)
        self.assertEqual(n_20, 20)
        self.assertEqual(n_80, 60)
        self.assertEqual(n_100, 20)


if __name__ == "__main__":
    unittest.main(failfast=True)
