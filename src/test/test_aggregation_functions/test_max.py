import sys
from pathlib import Path
import unittest

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql import functions as func
from models import D


class TestConcat(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Max(
            "concat-for-table",
            D.data_d,
            "-",
            D.data_d,
        )

        query = "CONCAT(d.data_d, '-', d.data_d) AS `concat-for-table`"

        self.assertEqual(concat.query, query)


if __name__ == "__main__":
    unittest.main()
