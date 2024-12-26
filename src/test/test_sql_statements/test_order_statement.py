from __future__ import annotations
import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda.common.interfaces import IRepositoryBase, IStatements_two_generic

from ormlambda import OrderType, Table, BaseModel, Column

DDBBNAME = "__test_ddbb__"


class TestOrder(Table):
    __table_name__ = "order_table_test"
    pk: int = Column(int, is_primary_key=True, is_auto_increment=True)
    a: int
    b: int
    c: int


class TestOrderModel(BaseModel[TestOrder]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]) -> IStatements_two_generic[TestOrder, TRepo]:
        return super().__new__(cls, TestOrder, repository)


class TestSQLStatements(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)
        cls.ddbb.create_database(DDBBNAME, "replace")
        cls.ddbb.database = DDBBNAME

        cls.tmodel = TestOrderModel(cls.ddbb)
        cls.tmodel.create_table()
        cls.tmodel.insert(
            (
                TestOrder(None, 1, 1, 1),
                TestOrder(None, 1, 2, 1),
                TestOrder(None, 1, 3, 2),
                TestOrder(None, 1, 3, 3),
                TestOrder(None, 1, 3, 4),
                TestOrder(None, 1, 4, 5),
                TestOrder(None, 2, 5, 6),
                TestOrder(None, 2, 6, 7),
                TestOrder(None, 2, 7, 8),
                TestOrder(None, 3, 8, 9),
            )
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_database(DDBBNAME)

    def test_order(self):
        query = self.tmodel.order(lambda x: (x.a, x.b, x.c), [OrderType.ASC, OrderType.DESC, OrderType.ASC]).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (1, 4, 5),
            (1, 3, 2),
            (1, 3, 3),
            (1, 3, 4),
            (1, 2, 1),
            (1, 1, 1),
            (2, 7, 8),
            (2, 6, 7),
            (2, 5, 6),
            (3, 8, 9),
        )
        self.assertTupleEqual(tuple_, query)

    def test_order_with_strings(self):
        query = self.tmodel.order(lambda x: (x.a, x.b, x.c), ["ASC", "DESC", "ASC"]).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (1, 4, 5),
            (1, 3, 2),
            (1, 3, 3),
            (1, 3, 4),
            (1, 2, 1),
            (1, 1, 1),
            (2, 7, 8),
            (2, 6, 7),
            (2, 5, 6),
            (3, 8, 9),
        )
        self.assertTupleEqual(tuple_, query)

    def test_order_with_strings_and_enums(self):
        query = self.tmodel.order(lambda x: (x.a, x.b, x.c), ["ASC", OrderType.DESC, "ASC"]).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (1, 4, 5),
            (1, 3, 2),
            (1, 3, 3),
            (1, 3, 4),
            (1, 2, 1),
            (1, 1, 1),
            (2, 7, 8),
            (2, 6, 7),
            (2, 5, 6),
            (3, 8, 9),
        )
        self.assertTupleEqual(tuple_, query)

    def test_order_by_first_column(self):
        query = self.tmodel.order(lambda x: x.a, OrderType.ASC).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (1, 1, 1),
            (1, 2, 1),
            (1, 3, 2),
            (1, 3, 3),
            (1, 3, 4),
            (1, 4, 5),
            (2, 5, 6),
            (2, 6, 7),
            (2, 7, 8),
            (3, 8, 9),
        )
        self.assertTupleEqual(tuple_, query)

    def test_order_by_second_column(self):
        query = self.tmodel.order(lambda x: x.b, OrderType.DESC).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (3, 8, 9),
            (2, 7, 8),
            (2, 6, 7),
            (2, 5, 6),
            (1, 4, 5),
            (1, 3, 2),
            (1, 3, 3),
            (1, 3, 4),
            (1, 2, 1),
            (1, 1, 1),
        )
        self.assertTupleEqual(tuple_, query)

    def test_order_by_third_column(self):
        query = self.tmodel.order(lambda x: x.c, OrderType.DESC).select(
            lambda x: (x.a, x.b, x.c),
            flavour=tuple,
        )

        tuple_ = (
            (3, 8, 9),
            (2, 7, 8),
            (2, 6, 7),
            (2, 5, 6),
            (1, 4, 5),
            (1, 3, 4),
            (1, 3, 3),
            (1, 3, 2),
            (1, 1, 1),
            (1, 2, 1),
        )
        self.assertTupleEqual(tuple_, query)


if __name__ == "__main__":
    unittest.main()
