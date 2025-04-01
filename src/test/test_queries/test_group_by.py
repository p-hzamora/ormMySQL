import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql import functions as func
from test.models import D


class TestGroupBy(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Concat(
            D,
            lambda d: (
                d.data_d,
                "-",
                d.data_d,
                func.Concat(D, lambda d: ("main", d.data_d), alias_name="main_data"),
            ),
        )

        query = "CONCAT(d.data_d, '-', d.data_d, d.CONCAT('main', d.data_d) as `main_data`) as `CONCAT`"

        self.assertEqual(concat.query, query)


if __name__ == "__main__":
    unittest.main()
