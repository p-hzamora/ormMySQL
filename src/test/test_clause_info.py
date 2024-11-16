from datetime import datetime
import sys
from pathlib import Path
import unittest
from parameterized import parameterized

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.databases.my_sql.clauses.ST_AsText import ST_AsText
from ormlambda.common.abstract_classes.clause_info import ClauseInfo

from models import A


class TestClauseInfo(unittest.TestCase):
    def test_passing_only_table(self):
        ci = ClauseInfo[A](A)
        self.assertEqual(ci.query, "a")

    def test_passing_only_table_with_alias_table(self):
        ci = ClauseInfo[A](A, alias_table=lambda x: "custom_table_name")
        self.assertEqual(ci.query, "`custom_table_name`")

    def test_passing_only_table_with_alias_table_placeholder_of_column(self):
        ci = ClauseInfo[A](A, alias_table=lambda x: "{column}")
        self.assertEqual(ci.query, "``")

    def test_passing_only_table_with_alias_table_placeholder_of_table(self):
        ci = ClauseInfo[A](A, alias_table=lambda x: "{table}")
        self.assertEqual(ci.query, "`a`")

    def test_constructor(self):
        ci = ClauseInfo[A](A, A.pk_a)
        self.assertEqual(ci.query, "a.pk_a")

    def test_passing_string(self):
        ci = ClauseInfo[A](A, "custom_column")
        self.assertEqual(ci.query, "a.custom_column")

    def test_passing_callable_alias_clause(self):
        ci = ClauseInfo[A](A, A.name_a, alias_clause=lambda x: "resolver_with_lambda_{column}")
        self.assertEqual(ci.query, "a.name_a AS `resolver_with_lambda_name_a`")

    def test_passing_string_with_placeholder_alias_clause(self):
        ci = ClauseInfo[A](A, A.name_a, alias_clause="resolver_with_lambda_{column}")
        self.assertEqual(ci.query, "a.name_a AS `resolver_with_lambda_name_a`")

    def test_passing_callable_alias_clause_with_placeholder(self):
        ci = ClauseInfo[A](A, A.name_a, alias_clause=lambda x: "resolver_with_lambda_{table}")
        self.assertEqual(ci.query, "a.name_a AS `resolver_with_lambda_a`")

    @parameterized.expand(
        (
            (A.pk_a, "pk_a", int),
            (A.name_a, "name_a", str),
            (A.data_a, "data_a", str),
            (A.date_a, "date_a", datetime),
            (A.value, "value", str),
        )
    )
    def test_passing_callable_and_custom_method(self, column, string_col: str, result: object):
        def message_placeholder(ci: ClauseInfo[A]):
            return ci.dtype.__name__

        ci = ClauseInfo[A](A, column, alias_clause=message_placeholder)
        self.assertEqual(ci.query, f"a.{string_col} AS `{result.__name__}`")

    def test_passing_callable_alias_table(self):
        ci = ClauseInfo[A](A, A.date_a, alias_table=lambda x: "custom_alias_for_{table}_table")
        self.assertEqual(ci.query, "`custom_alias_for_a_table`.date_a")

    def test_passing_callable_alias_table_with_placeholder(self):
        ci = ClauseInfo[A](A, A.date_a, alias_table=lambda x: "custom_alias_for_{column}_column")
        self.assertEqual(ci.query, "`custom_alias_for_date_a_column`.date_a")

    def test_passing_asterisk(self):
        ci = ClauseInfo[A](A, "*")
        self.assertEqual(ci.query, "a.pk_a, a.name_a, a.data_a, a.date_a, a.value")

    def test_passing_table(self):
        ci = ClauseInfo[A](A, A)
        self.assertEqual(ci.query, "a.pk_a, a.name_a, a.data_a, a.date_a, a.value")

    def test_passing_alias_table(self):
        ci = ClauseInfo[A](A, A.data_a, "ALIAS_TABLE")
        self.assertEqual(ci.query, "`ALIAS_TABLE`.data_a")

    def test_passing_alias_clause(self):
        ci = ClauseInfo[A](A, A.data_a, None, "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query, "a.data_a AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_with_alias_table_and_alias_clause(self):
        ci = ClauseInfo[A](A, A.pk_a, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query, "`ALIAS_TABLE`.pk_a AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_for_all_columns_with_alias_table_and_alias_clause(self):
        ci = ClauseInfo[A](A, A, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query, "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_for_all_columns_with_asterisk_with_alias_table_and_alias_clause(self):
        ci = ClauseInfo[A](A, "*", "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query, "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_passing_aggregation_method(self):
        ci_a = ClauseInfo[A](A, A.data_a)
        ci = ClauseInfo[A](A, aggregation_method=ST_AsText(ci_a), alias_clause="cast_point")

        self.assertEqual(ci.query, "ST_AsText(a.data_a) AS `cast_point`")


if __name__ == "__main__":
    unittest.main()
