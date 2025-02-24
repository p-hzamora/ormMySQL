import sys
from pathlib import Path
import unittest



sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.common.abstract_classes.clause_info import ClauseInfo
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql.clauses import Alias


# from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from models import D, Address, City


class TestAlias(unittest.TestCase):
    def test_alias_without_aliases(self) -> None:
        query = "d.data_d"
        self.assertEqual(
            Alias(ClauseInfo(D.data_d)).query,
            query,
        )

    def test_alias_with_alias_table(self) -> None:
        query = "`other_name`.data_d"
        self.assertEqual(
            Alias(ClauseInfo(D.data_d, alias_table="other_name")).query,
            query,
        )

    def test_alias_with_clause_table(self) -> None:
        query = "d.data_d AS `other_name`"
        self.assertEqual(
            Alias(ClauseInfo(D.data_d, alias_clause="other_name")).query,
            query,
        )

    def test_alias_passing_only_table(self) -> None:
        query = "`other_name`.pk_d, `other_name`.data_d, `other_name`.fk_c, `other_name`.fk_extra_c"
        self.assertEqual(
            Alias(ClauseInfo(D, alias_table="other_name")).query,
            query,
        )

    def test_alias_passing_only_table_with_both_aliases(self) -> None:
        query = "`other_name`.* AS `name_for_column`"
        self.assertEqual(
            Alias(ClauseInfo(D, alias_table="other_name", alias_clause="name_for_column")).query,
            query,
        )

    def test_AAalias_passing_only_table_with_context(self) -> None:
        ctx = ClauseInfoContext(table_context={
            City:'ctx_name_for_address'
        })
        query = "`ctx_name_for_address`.city_id AS `alias-name`"
        self.assertEqual(
            Alias(ClauseInfo(
                Address.City.city_id,
                alias_table="another_custom_alias",
                alias_clause="{table}~{column}",
                context=ctx,
            ),alias_clause="alias-name").query,
            query,
        )

    def test_alias_passing_aggregate_function(self) -> None:
        ctx = ClauseInfoContext(table_context={
            City:'ctx_name_for_address'
        })
        query = "`ctx_name_for_address`.city_id AS `city~city_id`"
        self.assertEqual(
            Alias(ClauseInfo(
                Address.City.city_id,
                alias_table="another_custom_alias",
                alias_clause="{table}~{column}",
                context=ctx,
            )).query,
            query,
        )

    


if __name__ == "__main__":
    unittest.main()
