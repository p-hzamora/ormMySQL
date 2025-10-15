import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import Count

from test.models import D
from ormlambda.dialects import mysql
from ormlambda import TableProxy
from ormlambda.common import GlobalChecker

DIALECT = mysql.dialect


class TestCount(unittest.TestCase):
    def test_count_passing_asterisk(self) -> None:
        query = "COUNT(*) AS `count`"
        self.assertEqual(Count("*").compile(DIALECT).string, query)

    def test_count_with_D_table(self) -> None:
        query = "COUNT(*) AS `count`"
        self.assertEqual(Count(TableProxy(D)).compile(DIALECT).string, query)

    def test_count_with_D_table_and_passing_table_context(self) -> None:
        query = "COUNT(*) AS `count`"
        self.assertEqual(Count(TableProxy(D.C.B.A)).compile(DIALECT).string, query)

    def test_count_passing_column(self) -> None:
        query = "COUNT(`d`.data_d) AS `other_name`"
        col = GlobalChecker[D].resolved_callback_object(D, lambda x: x.data_d)[0]
        self.assertEqual(Count(col, alias="other_name").compile(DIALECT).string, query)


if __name__ == "__main__":
    unittest.main()
