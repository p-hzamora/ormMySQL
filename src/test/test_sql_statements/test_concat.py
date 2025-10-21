from __future__ import annotations
import pytest

from pydantic import BaseModel

from test.models import Address  # noqa: F401
from ormlambda import ORM, Concat, IStatements


@pytest.fixture(autouse=True)
def amodel(sakila_engine) -> None:  # noqa: F811
    return ORM(Address, sakila_engine)


def test_concat(amodel: IStatements[Address]):
    class QueryResponse(BaseModel):
        address: str
        city: str
        concat: str

    # fmt: off
    concat = (
        amodel
        .where(lambda x: x.City.Country.country.regex(r"^Spain"))
        .first(lambda x: (
            x.address,
            x.City.city,
            Concat(
                (
                    "Address: ",
                    x.address,
                    " - city: ",
                    x.City.city,
                    " - country: ",
                    x.City.Country.country,
                ),
                alias="concat",
            ),
        ),
        flavour=QueryResponse,
    )
    )
    # fmt: on

    res = QueryResponse(
        address="939 Probolinggo Loop",
        city="A Coruña (La Coruña)",
        concat="Address: 939 Probolinggo Loop - city: A Coruña (La Coruña) - country: Spain",
    )
    assert concat == res


def test_concat_without_lambda(amodel: IStatements[Address]):
    concat = amodel.where(lambda x: x.City.Country.country.regex(r"^Spain")).first(
        lambda x: (
            x.address,
            x.City.city,
            Concat(
                (
                    "Address: ",
                    x.address,
                    " - city: ",
                    x.City.city,
                    " - country: ",
                    x.City.Country.country,
                ),
                alias="CONCAT",
            ),
        ),
        flavour=dict,
    )

    res = {
        "address": "939 Probolinggo Loop",
        "city": "A Coruña (La Coruña)",
        "CONCAT": "Address: 939 Probolinggo Loop - city: A Coruña (La Coruña) - country: Spain",
    }
    assert concat == res
