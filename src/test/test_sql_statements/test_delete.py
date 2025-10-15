from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM
from test.models import (
    TestTable,
)  # noqa: E402


from test.config import create_env_engine, create_engine_for_db


DDBBNAME = "__test_ddbb__"
TABLETEST = TestTable.__table_name__


def create_instance_of_TestTable(number: int) -> list[TestTable]:
    if number <= 0:
        number = 1
    return [TestTable(*[x] * len(TestTable.__annotations__)) for x in range(1, number + 1)]


class TestDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_env_engine()

        cls.ddbb.create_schema(DDBBNAME, "replace")
        cls.ddbb = create_engine_for_db(DDBBNAME)
        cls.tmodel = ORM(TestTable, cls.ddbb)
        cls.tmodel.create_table("replace")

    def tearDown(self) -> None:
        self.tmodel.delete()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_schema(DDBBNAME)

    def test_delete(self):
        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.where(lambda x: x.Col1 == 2).delete()
        select_all = self.tmodel.select(lambda x: x.Col1, flavour=tuple)
        self.assertTupleEqual((1, 3, 4, 5), select_all)

    def test_delete_passing_instance(self):
        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.delete(TestTable(2))
        select_all = self.tmodel.select(lambda x: x.Col1, flavour=tuple)
        self.assertTupleEqual((1, 3, 4, 5), select_all)

    def test_delete_passing_list_of_instance(self):
        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.delete(
            [
                TestTable(2),
                TestTable(3),
                TestTable(4),
            ]
        )
        select_all = self.tmodel.select(lambda x: x.Col1, flavour=tuple)
        self.assertTupleEqual((1, 5), select_all)


if __name__ == "__main__":
    unittest.main(failfast=True)
