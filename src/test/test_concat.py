import sys
from pathlib import Path
import unittest

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.databases.my_sql import functions as func

from models import D


class TestConcat(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Concat(
            D,
            lambda d: (d.data_d, "-", d.data_d),
            alias=True,
        )

        query = "CONCAT(d.data_d, '-', d.data_d) as `CONCAT`"

        self.assertEqual(concat.query, query)


if __name__ == "__main__":
    unittest.main()
