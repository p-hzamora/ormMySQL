from test.models import (  # noqa: E402
    City,
    Country,
)

from ormlambda import ORM


def test_constructor(sakila_engine):
    city = ORM(City, sakila_engine)
    country = ORM(Country, sakila_engine)

    rusult_ci = city.select(flavour=set)
    result_co = country.select(flavour=set)

    assert isinstance(rusult_ci, tuple)
    assert isinstance(rusult_ci[0], set)

    assert isinstance(result_co, tuple)
    assert isinstance(result_co[0], set)
