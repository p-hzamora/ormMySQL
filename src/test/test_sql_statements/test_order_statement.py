from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from ormlambda import OrderType, Table, ORM, Column

DDBBNAME = "__test_ddbb__"


class TestOrder(Table):
    __table_name__ = "order_table_test"
    pk: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    a: Column[int]
    b: Column[int]
    c: Column[int]


class TestSQLStatements(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_env_engine()
        cls.ddbb.create_schema(DDBBNAME, "replace")
        cls.ddbb = create_engine_for_db(DDBBNAME)

        cls.tmodel = ORM(TestOrder, cls.ddbb)
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
        cls.ddbb.drop_schema(DDBBNAME)

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
