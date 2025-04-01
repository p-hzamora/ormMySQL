import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.models import A


class TestClauseInfo(unittest.TestCase):
    def test_passing_only_table(self):
        self.assertEqual(A.pk_a.table, A)


if __name__ == "__main__":
    unittest.main()
