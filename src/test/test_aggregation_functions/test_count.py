import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql.clauses import Count

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from test.models import D


class TestCount(unittest.TestCase):
    def test_count_passing_asterisk(self) -> None:
        query = "COUNT(*) AS `count`"
        self.assertEqual(Count("*").query, query)

    def test_count_with_D_table(self) -> None:
        query = "COUNT(*) AS `count`"
        self.assertEqual(Count(D).query, query)

    def test_count_with_D_table_and_passing_table_context(self) -> None:
        ctx = ClauseInfoContext(table_context={D: "new-d-table"})
        query = "COUNT(`new-d-table`.*) AS `count`"
        self.assertEqual(Count(D, alias_table="{table}", context=ctx).query, query)

    def test_count_passing_column(self) -> None:
        query = "COUNT(data_d) AS `other_name`"
        self.assertEqual(Count(D.data_d, alias_clause="other_name").query, query)

    def test_count_passing_column_with_context(self) -> None:
        ctx = ClauseInfoContext(table_context={D: "new-d-table"})
        query = "COUNT(`new-d-table`.data_d) AS `other_name`"
        self.assertEqual(Count(D.data_d, alias_table="{table}", alias_clause="other_name", context=ctx).query, query)


if __name__ == "__main__":
    unittest.main()
