import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.clauses import Alias
from ormlambda.common import GlobalChecker


# from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from test.models import D
from ormlambda.dialects import mysql

DIALECT = mysql.dialect


class TestAlias(unittest.TestCase):
    def test_alias_without_aliases(self) -> None:
        with self.assertRaises(TypeError):
            Alias(D.data_d)

    def test_alias_passing_only_table(self) -> None:
        query = "`d`.data_d AS `name_for_column`"

        column = GlobalChecker[D].resolved_callback_object(D, lambda x: x.data_d)
        self.assertEqual(
            Alias(*column, alias="name_for_column").compile(DIALECT).string,
            query,
        )


if __name__ == "__main__":
    unittest.main()
