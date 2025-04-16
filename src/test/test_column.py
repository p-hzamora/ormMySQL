import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.column import Column
from test.models import A


class TestColumn(unittest.TestCase):
    def test_passing_only_table(self):
        self.assertEqual(A.pk_a.table, A)

    def test_comparing_column_hashes_and_failed(self):
        EXPECTED = Column(str)
        column = Column(column_name="x-name")

        with self.assertRaises(AssertionError):
            self.assertEqual(hash(EXPECTED), hash(column))

    def test_comparing_column_hashes_and_success(self):
        EXPECTED = Column(str, column_name="x-name")
        column = Column(column_name="x-name")
        self.assertEqual(hash(EXPECTED), hash(column))


if __name__ == "__main__":
    unittest.main()
