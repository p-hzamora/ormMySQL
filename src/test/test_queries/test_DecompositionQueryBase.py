import unittest
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql.clauses.alias import Alias
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
from models import Address


class TestQueryBuilder(unittest.TestCase):
    def test_QueryBuilder_constructor(self):
        ctx = ClauseInfoContext()
        mysql = DecompositionQueryBase(
            Address,
            columns=(
                "a",
                Alias(Address, "custom_alias", context=ctx),
                Alias(Address.City.city, alias_table="another_custom_alias", alias_clause="{table}~{column}", context=ctx),
                Address.address,
                Address.City.Country.country_id,
            ),
            context=ctx,
        )
        pass


if __name__ == "__main__":
    unittest.main()
