import pytest


from test.conftest import sakila_engine  # noqa: E402
from ormlambda.dialects import mysql
from test.models import Address, City, Country
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine

DIALECT = mysql.dialect


@pytest.fixture
def model(sakila_engine: Engine) -> IStatements[Address]:
    return ORM(Address, sakila_engine)


def test_select_all(model: IStatements[Address]):
    res1 = model.select()
    res2 = model.select(lambda x: x)
    res3 = model.select(lambda x: (x,))

    assert isinstance(res1, tuple)
    assert isinstance(res1[0], Address)
    assert res1 == res2
    assert res2 == res3


def test_select_all_different_tables(model: IStatements[Address]):
    res1 = model.select(
        lambda x: (
            x,
            x.City,
            x.City.Country,
        ),
        avoid_duplicates=True,
    )

    assert isinstance(res1, tuple)
    assert isinstance(res1[0][0], Address)
    assert isinstance(res1[0][1], City)
    assert isinstance(res1[0][2], Country)

    for a, ci, co in res1:
        assert a.city_id == ci.city_id
        assert ci.country_id == co.country_id
