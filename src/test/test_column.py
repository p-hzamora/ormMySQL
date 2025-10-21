from ormlambda.sql.column import Column
from test.models import A


def test_passing_only_table():
    assert A.pk_a.table==A


def test_comparing_column_hashes_and_failed():
    EXPECTED = Column(str)
    column = Column(column_name="x-name")

    assert hash(EXPECTED) != hash(column)


def test_comparing_column_hashes_and_success():
    EXPECTED = Column(str, column_name="x-name")
    column = Column(column_name="x-name")
    assert hash(EXPECTED)== hash(column)
