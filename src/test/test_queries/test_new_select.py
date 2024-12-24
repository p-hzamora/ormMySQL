import unittest
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from models import D  # noqa: E402


from ormlambda.databases.my_sql.clauses.select import Select
from ormlambda.databases.my_sql import functions as func


class TestSelect(unittest.TestCase):
    def test_select_with_context(self):
        context = ClauseInfoContext()
        select = Select[D](
            D,
            columns=(
                D.C,
                D.C.B,
                D.C.B.A,
                func.Concat((D.pk_d, "-", D.data_d), context=context),
            ),
            context=context,
        )

        query:str = "SELECT `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, `c_fk_b_pk_b`.pk_b AS `b_pk_b`, `c_fk_b_pk_b`.data_b AS `b_data_b`, `c_fk_b_pk_b`.fk_a AS `b_fk_a`, `c_fk_b_pk_b`.data AS `b_data`, `b_fk_a_pk_a`.pk_a AS `a_pk_a`, `b_fk_a_pk_a`.name_a AS `a_name_a`, `b_fk_a_pk_a`.data_a AS `a_data_a`, `b_fk_a_pk_a`.date_a AS `a_date_a`, `b_fk_a_pk_a`.value AS `a_value`, CONCAT(`d`.pk_d, '-', `d`.data_d) AS `concat` FROM d AS `d` INNER JOIN c AS `d_fk_c_pk_c` ON `d`.fk_c = `d_fk_c_pk_c`.pk_c INNER JOIN b AS `c_fk_b_pk_b` ON `d_fk_c_pk_c`.fk_b = `c_fk_b_pk_b`.pk_b INNER JOIN a AS `b_fk_a_pk_a` ON `c_fk_b_pk_b`.fk_a = `b_fk_a_pk_a`.pk_a"

        self.assertEqual(select.query, query)


if "__main__" == __name__:
    unittest.main()
