from __future__ import annotations

from test.models import Address  # noqa: F401
from ormlambda import IStatements

import re


class RegexFilter:
    def __init__(self, pattern: str, value: str, *kwargs) -> None:
        self._compile: re.Pattern = re.compile(pattern, *kwargs)
        self._value: str = value


def test_one_where(amodel: IStatements[Address]):
    co = "Spain"
    # fmt: off
    select = (
        amodel.offset(3)
        .where(lambda x: x.City.Country.country == co)
        .limit(2)
        .order(lambda x: x.City.city, "ASC")
        .select(lambda x: x.City.city,flavour=tuple)
    )
    # fmt: on

    res = (
        ("Ourense (Orense)"),
        ("Santiago de Compostela"),
    )
    assert select == res


def test_multiple_wheres_using_lambda(amodel: IStatements[Address]) -> None:
    city = "Ourense (Orense)"
    country = r"[sS]pain"

    result = amodel.where(
        lambda x: (
            x.City.Country.country.regex(country),
            x.City.city == city,
        )
    ).select(
        lambda x: (
            x.City.city,
            x.City.Country.country,
        ),
        flavour=dict,
    )

    assert len(result) == 1
    assert result[0], {"city": "Ourense (Orense)", "country": "Spain"}


def test_pass_multiples_where_clause(amodel: IStatements[Address]):
    city = "Ourense (Orense)"
    country = r"[sS]pain"

    # fmt: off
    result = (
        amodel
        .where(lambda x: x.City.Country.country.regex(country))
        .where(lambda x: x.City.city == city)
        .select(lambda x: (
                x.City.city,
                x.City.Country.country,
            ),
            flavour=dict,
        )
        
    )

    # fmt: on

    assert len(result) == 1
    assert result[0] == {"city": "Ourense (Orense)", "country": "Spain"}
