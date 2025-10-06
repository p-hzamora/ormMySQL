import sys
from pathlib import Path
from typing import Any, Callable
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import Concat
from test.models import D

from ormlambda.dialects import mysql
from ormlambda.common import GlobalChecker

DIALECT = mysql.dialect


def wrapped_query(mth: Callable[[D], tuple[Any]]):
    return GlobalChecker[D].resolved_callback_object(D, mth)[0]


class TestConcat(unittest.TestCase):
    def test_Concat(self) -> None:
        def lambda_query(d: D):
            return Concat(
                (d.data_d, "-", d.data_d),
                alias="concat-for-table",
            )

        concat = wrapped_query(lambda_query)

        query = "CONCAT(`d`.data_d, '-', `d`.data_d) AS `concat-for-table`"

        query = concat.compile(DIALECT).string
        self.assertEqual(query, query)

    def test_concat_passing_table(self):
        concat = wrapped_query(lambda x: Concat(x))
        mssg: str = "CONCAT(`d`.pk_d, `d`.data_d, `d`.fk_c, `d`.fk_extra_c) AS `concat`"
        query = concat.compile(DIALECT).string
        self.assertEqual(query, mssg)

    def test_raise_ValueError_when_passing_ForeignKey(self):
        with self.assertRaises(ValueError) as err:
            Concat((D.C))
        str(err.exception)

    def test_concat_passing_ForeignKey(self):
        concat = wrapped_query(lambda x: Concat((x.C)))

        mssg: str = "CONCAT(`d_C`.pk_c, `d_C`.data_c, `d_C`.fk_b) AS `concat`"
        query = concat.compile(DIALECT).string

        self.assertEqual(query, mssg)

    def test_concat_passing_ForeignKey_with_context(self):
        columns = GlobalChecker[D].resolved_callback_object(D, lambda x: x.C)
        concat = Concat(columns)
        mssg: str = "CONCAT(`d_C`.pk_c, `d_C`.data_c, `d_C`.fk_b) AS `concat`"
        query = concat.compile(DIALECT).string
        self.assertEqual(query, mssg)


if __name__ == "__main__":
    unittest.main()
