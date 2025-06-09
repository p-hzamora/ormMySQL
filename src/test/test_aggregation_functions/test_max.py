import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql import functions as func
from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from test.models import D

from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def MaxMySQL(*args, **kwargs) -> func.Max:
    return func.Max(*args, **kwargs, dialect=DIALECT)


class TestMax(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = MaxMySQL(
            alias_clause="concat-for-table",
            elements=(
                D.data_d,
                D.fk_c,
                D.pk_d,
            ),
        )

        query = "MAX(d.data_d, d.fk_c, d.pk_d) AS `concat-for-table`"

        self.assertEqual(concat.query, query)

    def test_Concat_with_context(self) -> None:
        context = ClauseInfoContext(table_context={D: "new-d-table"})
        concat = MaxMySQL(
            alias_clause="concat-for-table",
            elements=(
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
