from __future__ import annotations
import pytest


from test.models import Address  # noqa: F401
from ormlambda import ORM
from pydantic import BaseModel
from ormlambda import Min, Max, IStatements


@pytest.fixture
def amodel(sakila_engine) -> IStatements[Address]:  # noqa: F811
    return ORM(Address, sakila_engine)


def test_max_and_min(amodel: IStatements[Address]) -> None:
    # fmt: off
    res = (
        amodel
        .where(lambda x: (
            x.address_id <= 200,
            x.address_id >= 100))
        .first(lambda x: (
            Max(x.address_id),
            Min(x.address_id),
            ),
            flavour=dict,
        )
    )
    # fmt: on

    assert res["max"] == 200
    assert res["min"] == 100


def test_max_min_with_aliases(amodel: IStatements[Address]) -> None:
    class MaxMinResponse(BaseModel):
        addressIdMax: int
        addressIdMin: int

    # fmt: off
    res = (
        amodel
        .where(lambda x: (x.address_id <= 200, x.address_id >= 100))
        .first(lambda x: (
            Max(x.address_id, "addressIdMax"),
            Min(x.address_id, "addressIdMin"),
            ),
            flavour=MaxMinResponse,
        )
    )
    # fmt: off
    assert res.addressIdMax==200
    assert res.addressIdMin==100


def test_max_with_lambda(amodel: IStatements[Address]) -> None:
    res1 = amodel.groupby(lambda x: x.address_id).max(lambda x: x.address_id)
    res2 = amodel.groupby(lambda x: x.address_id).max(lambda x: x.address_id)

    assert res1 == res2


def test_min_with_lambda(amodel: IStatements[Address]) -> None:
    res1 = amodel.groupby(lambda x: x.address_id).min(lambda x: x.address_id)
    res2 = amodel.groupby(lambda x: x.address_id).min(lambda x: x.address_id)

    assert res1 == res2


def test_sum_with_lambda(amodel: IStatements[Address]) -> None:
    res1 = amodel.groupby(lambda x: x.address_id).sum(lambda x: x.address_id)
    res2 = amodel.groupby(lambda x: x.address_id).sum(lambda x: x.address_id)

    assert res1 == res2
