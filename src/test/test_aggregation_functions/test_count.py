from ormlambda import Count

from test.models import D
from ormlambda.dialects import mysql
from ormlambda import TableProxy
from ormlambda.common import GlobalChecker

DIALECT = mysql.dialect


def test_count_passing_asterisk() -> None:
    query = "COUNT(*) AS `count`"
    assert Count("*").compile(DIALECT).string == query


def test_count_with_D_table() -> None:
    query = "COUNT(*) AS `count`"
    assert Count(TableProxy(D)).compile(DIALECT).string == query


def test_count_with_D_table_and_passing_table_context() -> None:
    query = "COUNT(*) AS `count`"
    assert Count(TableProxy(D.C.B.A)).compile(DIALECT).string == query


def test_count_passing_column() -> None:
    query = "COUNT(`d`.data_d) AS `other_name`"
    col = GlobalChecker[D].resolved_callback_object(D, lambda x: x.data_d)[0]
    assert Count(col, alias="other_name").compile(DIALECT).string == query
