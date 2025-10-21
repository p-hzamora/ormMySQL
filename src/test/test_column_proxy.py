from ormlambda.sql.column_table_proxy import FKChain
from ormlambda.sql.column import ColumnProxy

from test.test_sql_statements.test_multiples_references_to_the_same_table import A


def test_column_proxy() -> None:
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

    assert column_proxy.path.steps == [
        A.B1,
        A.B1.C1,
        A.B1.C1.D1,
    ]
