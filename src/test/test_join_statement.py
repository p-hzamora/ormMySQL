from __future__ import annotations
import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection
from datetime import datetime


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import IRepositoryBase  # noqa: E402

from models import (
    TestTable,
    ModelAB,
    A,
    B,
)  # noqa: E402

DDBBNAME = "__test_ddbb__"
TABLETEST = TestTable.__table_name__


def create_instance_of_TestTable(number: int) -> list[TestTable]:
    if number <= 0:
        number = 1
    return [TestTable(*[x] * len(TestTable.__annotations__)) for x in range(1, number + 1)]


class TestJoinStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)
        cls.ddbb.create_database(DDBBNAME, "replace")
        cls.ddbb.database = DDBBNAME

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_database(DDBBNAME)

    # FIXME [x]: Review this method in the future
    def test_join(self):
        """
        New way to use join with 'with' clause
        """
        modelA = ModelAB(A, self.ddbb)
        modelB = ModelAB(B, self.ddbb)

        a_insert = [A(x, "a", "data_a", datetime.today(), f"pk_with_value_{x}") for x in range(1, 6)]
        b_insert = [
            *[B(None, "data_b", 1, "pk_b_with_data_1") for x in range(20)],
            *[B(None, "data_b", 2, "pk_b_with_data_2") for x in range(10)],
            *[B(None, "data_b", 3, "pk_b_with_data_3") for x in range(5)],
            B(None, "data_b", 4, "pk_b_with_data_4"),
        ]

        modelA.create_table()
        modelB.create_table()
        modelA.insert(a_insert)
        modelB.insert(b_insert)

        modelB.select((A, B))


if __name__ == "__main__":
    unittest.main(failfast=False)
