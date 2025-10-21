import pytest

from ormlambda import ORM, Max, IStatements
from test.models import Address  # noqa: E402


@pytest.fixture
def amodel(sakila_engine) -> IStatements[Address]:  # noqa: F811
    return ORM(Address, sakila_engine)


def test_max_using_select_one(amodel: IStatements[Address]):
    max = amodel.select_one(lambda x: Max(x.address_id), flavour=dict)["max"]
    assert max == 605


def test_max_using_max(amodel: IStatements[Address]):
    max = amodel.max(lambda x: x.address_id)
    assert max == 605


def test_max_using_where_condition(amodel: IStatements[Address]):
    MAX_VALUE = 300
    result = amodel.where(lambda x: x.address_id <= MAX_VALUE).max(lambda x: x.address_id)
    assert result == MAX_VALUE
