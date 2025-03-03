import sys
from pathlib import Path
import unittest


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.databases.my_sql import functions as func
from models import D, C


class TestConcat(unittest.TestCase):
    def test_Concat(self) -> None:
        concat = func.Concat(
            alias_clause="concat-for-table",
            values=(
                D.data_d,
                "-",
                D.data_d,
            ),
        )

        query = "CONCAT(d.data_d, '-', d.data_d) AS `concat-for-table`"

        self.assertEqual(concat.query, query)

    def test_concat_passing_table(self):
        concat = func.Concat(values=(D))
        mssg: str = "CONCAT(d.pk_d, d.data_d, d.fk_c, d.fk_extra_c) AS `concat`"
        self.assertEqual(concat.query, mssg)

    def test_concat_passing_ForeignKey(self):
        concat = func.Concat(values=(D.C))
        mssg: str = "CONCAT(c.pk_c, c.data_c, c.fk_b) AS `concat`"
        self.assertEqual(concat.query, mssg)

    def test_concat_passing_ForeignKey_with_context(self):
        ctx = ClauseInfoContext(table_context={C: "alias-for-c"})
        concat = func.Concat(values=(D.C), context=ctx)
        mssg: str = "CONCAT(`alias-for-c`.pk_c, `alias-for-c`.data_c, `alias-for-c`.fk_b) AS `concat`"
        self.assertEqual(concat.query, mssg)


if __name__ == "__main__":
    unittest.main()
