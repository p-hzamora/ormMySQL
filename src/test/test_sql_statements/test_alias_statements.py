from __future__ import annotations

import pytest


from test.models import Address  # noqa: F401
from ormlambda import ORM, Alias, IStatements


@pytest.fixture
def amodel(sakila_engine) -> IStatements[Address]:  # noqa: F811
    return ORM(Address, sakila_engine)


def test_alias_with_alias_attribute(amodel: IStatements[Address]):
    res = amodel.where(lambda x: x.City.Country.country == "Spain").first(
        lambda x: (
            x.address_id,
            x.district,
            x.City.city,
            x.City.Country.country,
        ),
        flavour=dict,
        alias="{column}",
    )
    EXPECTED = {
        "address_id": 56,
        "district": "Galicia",
        "city": "A Coruña (La Coruña)",
        "country": "Spain",
    }
    assert res == EXPECTED


def test_alias_passing_alias_method(amodel: IStatements[Address]):
    res = amodel.where(lambda x: x.City.Country.country == "Spain").first(
        lambda x: (
            Alias(x.address_id, "{column}"),
            Alias(x.district, "{column}"),
            Alias(x.City.city, "{column}"),
            Alias(x.City.Country.country, "{column}"),
        ),
        flavour=dict,
    )
    EXPECTED = {
        "address_id": 56,
        "district": "Galicia",
        "city": "A Coruña (La Coruña)",
        "country": "Spain",
    }
    assert res == EXPECTED
