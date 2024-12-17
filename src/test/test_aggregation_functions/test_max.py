import sys
from pathlib import Path
import unittest


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.databases.my_sql import functions as func
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from models import D


class TestMax(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Max(
            alias_clause="concat-for-table",
            column=(
                D.data_d,
                D.fk_c,
                D.pk_d,
            ),
        )

        query = "MAX(d.data_d, d.fk_c, d.pk_d) AS `concat-for-table`"

        self.assertEqual(concat.query, query)

    def test_Concat_with_context(self) -> None:
        context = ClauseInfoContext(clause_context={D: "new-d-table"})
        concat = func.Max(
            alias_clause="concat-for-table",
            column=(
                D.data_d,
                D.fk_c,
                D.pk_d,
            ),
            context=context,
        )

        query = "MAX(`new-d-table`.data_d, `new-d-table`.fk_c, `new-d-table`.pk_d) AS `concat-for-table`"

        self.assertEqual(concat.query, query)


if __name__ == "__main__":
    unittest.main()
