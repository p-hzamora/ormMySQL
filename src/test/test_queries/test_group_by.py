import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql import functions as func
from test.models import D


class TestGroupBy(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Concat(
            (
                D.data_d,
                "-",
                D.data_d,
                func.Concat(("main", D.data_d), alias_clause="main_data"),
            ),
        )

        query = "CONCAT(d.data_d, '-', d.data_d, CONCAT('main', d.data_d) AS `main_data`) AS `concat`"

        self.assertEqual(concat.query, query)


if __name__ == "__main__":
    unittest.main()
