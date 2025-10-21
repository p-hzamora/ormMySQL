from __future__ import annotations
from typing import Optional
import pytest


from pydantic import BaseModel

from test.models import Address, City  # noqa: F401
from ormlambda import ORM, Count, OrderType, JoinType, Alias
from ormlambda.statements.interfaces import IStatements


@pytest.fixture
def cmodel(sakila_engine):
    return ORM(City, sakila_engine)


class Response(BaseModel):
    country: str
    sumCities: int


def query(cmodel: IStatements[City], char_to_filter: str, limit: Optional[int] = None, offset: int = 0) -> tuple[Response, ...] | Response:
    # fmt: off
    response = (
        cmodel
            .order(lambda x: x.sumCities, "DESC")
            .where(lambda x: x.Country.country.like(f"%{char_to_filter}%"))
            .groupby(lambda x: x.Country.country)
    )
    # fmt: on

    if limit:
        response.limit(limit)

    if offset:
        response.offset(offset)

    res = response.select(
        lambda x: (
            x.Country.country,
            Count(alias="sumCities"),
        ),
        flavour=Response,
    )
    return res[0] if len(res) == 1 else res


def test_complex_1(amodel: IStatements[Address]):
    class Response(BaseModel):
        pkCity: int
        count: int

    PK = 312
    # fmt:off
    res = (
        amodel.where(lambda x: x.City.city_id >= PK)
        .having(lambda x: x.count > 1)
        .groupby(lambda x: x.city_id)
        .select(
            lambda x: (
                Alias(x.City.city_id, "pkCity"),
                Count(x.address_id, "count"),
            ),
            flavour=Response,
        )
    )
    # fmt:on
    RESULT = (
        Response(pkCity=312, count=2),
        Response(pkCity=576, count=2),
    )
    assert res == RESULT


def test_extract_countries_with_white_space_in_the_name(cmodel):
    res = query(cmodel, "spain")
    assert res == Response(country="Spain", sumCities=5)


def test_dicctioanry_of_countries_with_commans_dots_and_white_spaces(cmodel):
    result = {}

    for char in " ", ".", ",":
        q = query(cmodel, char, limit=1)
        result[char] = q

    EXPECTED = {
        " ": Response(country="United States", sumCities=35),
        ".": Response(country="Virgin Islands, U.S.", sumCities=1),
        ",": Response(country="Congo, The Democratic Republic of the", sumCities=2),
    }
    assert result == EXPECTED


def test_get_country_with_more_address_registered(amodel: IStatements[Address]):
    class Response(BaseModel):
        countryName: str
        contar: int

    # fmt:off
    res = (
        amodel
        .order(lambda x: x.contar, OrderType.DESC)
        .groupby(lambda x: x.City.Country.country)
        .first(
            lambda x: (
                Alias(x.City.Country.country, "countryName"),
                Count(alias="contar"),
            ),
            flavour=Response,
            by=JoinType.LEFT_EXCLUSIVE,
        )
    )
    # fmt:on

    EXPECTED = Response(countryName="India", contar=60)
    assert res == EXPECTED
