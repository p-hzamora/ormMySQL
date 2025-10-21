from ormlambda.sql import functions as func
from ormlambda.sql.context import PATH_CONTEXT
from test.models import D

from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def test_Concat() -> None:
    concat = func.Max(
        alias_clause="concat-for-table",
        elements=(
            D.data_d,
            D.fk_c,
            D.pk_d,
        ),
    )

    query = "MAX(d.data_d, d.fk_c, d.pk_d) AS `concat-for-table`"

    assert concat.compile(DIALECT) == query


def test_Concat_with_context() -> None:
    context = PATH_CONTEXT.add_table_alias(D, "new-d-table")
    concat = func.Max(
        elements=(
            D.data_d,
            D.fk_c,
            D.pk_d,
        ),
        context=context,
    )

    query = "MAX(`new-d-table`.data_d, `new-d-table`.fk_c, `new-d-table`.pk_d) AS `concat-for-table`"

    assert concat.compile(DIALECT) == query
