import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.sql.clauses.alias import Alias


# from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from test.models import D, Address, City


class TestAlias(unittest.TestCase):
    def test_alias_without_aliases(self) -> None:
        with self.assertRaises(TypeError):
            Alias(D.data_d)

    def test_alias_with_alias_table(self) -> None:
        query = "`other_name`.data_d AS `custom-alias`"
        self.assertEqual(
            Alias(D.data_d, alias_table="other_name", alias_clause="custom-alias").query,
            query,
        )

    def test_alias_with_clause_table(self) -> None:
        query = "d.data_d AS `override-original-clause`"
        self.assertEqual(
            Alias(D.data_d, alias_clause="override-original-clause").query,
            query,
        )

    def test_alias_passing_only_table(self) -> None:
        query = "`other_name`.* AS `name_for_column`"
        self.assertEqual(
            Alias(D, D, alias_table="other_name", alias_clause="name_for_column").query,
            query,
        )

    def test_alias_passing_only_table_with_context(self) -> None:
        ctx = ClauseInfoContext(table_context={City: "ctx_name_for_address"})
        query = "`ctx_name_for_address`.city_id AS `alias-name`"
        self.assertEqual(
            Alias(
                Address.City.city_id,
                context=ctx,
                alias_clause="alias-name",
            ).query,
            query,
        )


if __name__ == "__main__":
    unittest.main()
