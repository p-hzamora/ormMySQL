import sys
from pathlib import Path
import unittest

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.databases.my_sql import functions as func
from ormlambda.databases.my_sql.clauses.new_select import Select
from models import D


class TestSelect(unittest.TestCase):
    def test_select(self):
        selected = Select(
            D,
            lambda d: (
                d,
                d.C.B.A.data_a,
                d.C,
                func.Concat(
                    D,
                    lambda d: (d.pk_d, "-", d.C.pk_c, "-", d.C.B.pk_b, "-", d.C.B.A, "-", d.C.B.data),
                    alias_name="concat_pks",
                ),
                func.Count(D, lambda x: x.C.B.A.name_a),
                func.Max(D, lambda x: x.C.B.A.data_a),
            ),
        )
        query_string: str = "SELECT d.pk_d as `d_pk_d`, d.data_d as `d_data_d`, d.fk_c as `d_fk_c`, d.fk_extra_c as `d_fk_extra_c`, a.data_a as `a_data_a`, c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, CONCAT(d.pk_d, '-', c.pk_c, '-', b.pk_b, '-', a.pk_a, a.name_a, a.data_a, a.date_a, a.value, '-', b.data) as `concat_pks`, COUNT(a.name_a) as `count`, MAX(a.data_a) as `max` FROM d INNER JOIN c ON d.fk_c = c.pk_c INNER JOIN b ON c.fk_b = b.pk_b INNER JOIN a ON b.fk_a = a.pk_a"
        self.assertEqual(selected.query, query_string)

    def test_select_with_select_inside(self) -> None:
        select = Select(
            D,
            lambda d: (
                d.C,
                func.Concat(D, lambda d: (d.pk_d, "-", d.data_d)),
            ),
        )

        query = "SELECT c.pk_c as `c_pk_c`, c.data_c as `c_data_c`, c.fk_b as `c_fk_b`, CONCAT(d.pk_d, '-', d.data_d) as `CONCAT` FROM d INNER JOIN c ON d.fk_c = c.pk_c"

        self.assertEqual(select.query, query)


if __name__ == "__main__":
    unittest.main()
