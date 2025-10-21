from ormlambda.sql.clauses import Alias
from ormlambda.common import GlobalChecker

import pytest

from test.models import D
from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def test_alias_without_aliases() -> None:
    with pytest.raises(TypeError):
        Alias(D.data_d)


def test_alias_passing_only_table() -> None:
    query = "`d`.data_d AS `name_for_column`"

    column = GlobalChecker[D].resolved_callback_object(D, lambda x: x.data_d)
    assert Alias(*column, alias="name_for_column").compile(DIALECT).string == query
