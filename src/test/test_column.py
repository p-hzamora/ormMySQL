import sys
from pathlib import Path
import unittest


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from models import A


class TestClauseInfo(unittest.TestCase):
    def test_passing_only_table(self):
        self.assertEqual(A.pk_a.table, A)


if __name__ == "__main__":
    unittest.main()
