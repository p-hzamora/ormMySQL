import pytest


from ormlambda.common import GlobalChecker

from test.test_sql_statements.test_multiples_references_to_the_same_table import A


@pytest.mark.skip("I don't know what this was created for")
def test_GlobalChecker():
    columns = GlobalChecker[A].resolved_callback_object(
        A,
        lambda a: (
            "string data",
            a.B1.C1.D1.name,
            a.B1.string_data,
            a.B1.C3.D2.pk_d,
        ),
    )

    columns

    return
