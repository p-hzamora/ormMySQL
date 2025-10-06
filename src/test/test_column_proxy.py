import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.column_table_proxy import FKChain
from ormlambda.sql.column import ColumnProxy

from test.config import create_env_engine
from ormlambda.dialects import mysql
from test.test_sql_statements.test_multiples_references_to_the_same_table import A


DIALECT = mysql.dialect
engine = create_env_engine()


class ColumnProxyTest(unittest.TestCase):
    def test_column_proxy(self) -> None:
        column_proxy = ColumnProxy(
            A.data_a,
            FKChain(
                A,
                [
                    A.B1,
                    A.B1.C1,
                    A.B1.C1.D1,
                ],
            ),
        )

        column_proxy.get_table_chain()
        column_proxy.get_full_chain()
        self.assertEqual(
            column_proxy.path.get_path_key(),
            [
                A.B1,
                A.B1.C1,
                A.B1.C1.D1,
            ],
        )

        column_proxy.get_relations("LEFT_JOIN", DIALECT)


if __name__ == "__main__":
    unittest.main()
