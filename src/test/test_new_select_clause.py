import sys
from pathlib import Path
import unittest

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.databases.my_sql import functions as func
from ormlambda.databases.my_sql.clauses.select import Select
from models import D


class TestSelect(unittest.TestCase):
    def test_select(self):
        selected = Select(
            D,
            lambda d: (
                d.C.B.A.data_a,
                d.C,
                func.Concat(
                    D,
                    lambda d: (
                        d.pk_d,
                        d.C.pk_c,
                        d.C.B.pk_b,
                        d.C.B.A.pk_a,
                    ),
                    alias="concat_pks",
                ),
                func.Count(D, lambda x: x.C.B.A.name_a),
                func.Max(D, lambda x: x.C.B.A.data_a),
            ),
        )
        query_string: str = "SELECT a.data_a as `a_data_a`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, CONCAT(d.pk_d, c.pk_c, b.pk_b, a.pk_a) as `concat_pks`, COUNT(a.name_a) as `count`, MAX(a.data_a) as `maximun` FROM d"
        self.assertEqual(selected.query, query_string)


if __name__ == "__main__":
    unittest.main()