import unittest
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from models import (  # noqa: E402
    D,
)


from ormlambda.databases.my_sql.clauses.select import Select
from ormlambda.databases.my_sql import functions as func
from ormlambda.databases.my_sql.clauses import Count


class TestSelect(unittest.TestCase):
    def test_AAselect_with_concat(self):
        ctx = ClauseInfoContext()
        selected = Select[D](
            D,
            lambda d: (
                func.Concat[D]((D.pk_d, "-", D.C.pk_c, "-", D.C.B.pk_b, "-", D.C.B.A, "-", D.C.B.data), alias_clause="concat_pks", context=ctx),
                d,
                d.C.B.A.data_a,
                d.C,
                Count(D.C.B.A.name_a, alias_table=lambda x: x.dtype, context=ctx),
                func.Max(D.C.B.A.data_a, context=ctx),
            ),
            context=ctx,
        )
        query_string: str = "SELECT CONCAT(`d`.pk_d, '-', `d_fk_c_pk_c`.pk_c, '-', b.pk_b, '-', `a`.pk_a, `a`.name_a, `a`.data_a, `a`.date_a, `a`.value, '-', b.data) AS `concat_pks`, `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c`, `a`.data_a AS `a_data_a`, `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, COUNT(`a`.*) AS `count`, MAX(`a`.data_a) AS `max` FROM d AS `d`"
        self.assertEqual(selected.query, query_string)


if "__main__" == __name__:
    unittest.main()
