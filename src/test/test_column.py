import sys
from pathlib import Path
import unittest


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.common.abstract_classes.comparer import Comparer
from ormlambda import Column, Table


class A(Table):
    __table_name__ = "a"
    pk: Column[int] = Column(int)


class TestClauseInfo(unittest.TestCase):
    def test_passing_only_table(self):
        self.assertEqual(A.pk.table, A)


class TestComparer(unittest.TestCase):
    def test_comparer(self) -> None:
        cond = A.pk == 100
        self.assertIsInstance(cond, Comparer)  # noqa: F821


if __name__ == "__main__":
    unittest.main()
