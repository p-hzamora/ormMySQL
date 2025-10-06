import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.common import GlobalChecker

from test.config import create_env_engine
from ormlambda.dialects import mysql
from test.test_sql_statements.test_multiples_references_to_the_same_table import A


DIALECT = mysql.dialect
engine = create_env_engine()


class ColumnProxyTest(unittest.TestCase):
    def test_GlobalChecker(self):
        # columns = GlobalChecker[A].resolved_callback_object(
        #     A,
        #     lambda a: (
        #         "string data",
        #         a.B1.C1.D1.name,
        #         a.B1.string_data,
        #         a.B1.C3.D2.pk_d,
        #     ),
        # )

        # columns

        return


if __name__ == "__main__":
    unittest.main()
