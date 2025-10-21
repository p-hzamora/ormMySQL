from typing import Callable
import pytest

from ormlambda.engine import Engine


from ormlambda import functions as func
from ormlambda import Alias
from ormlambda import ORM

from test.models import Address
from pydantic import BaseModel


class Response(BaseModel):
    max: int
    min: int
    sum: int
    avg: int
    abs: int
    ceil: int
    floor: int
    round: int
    pow: int
    sqrt: int
    mod: int
    rand: int
    truncate: int


@pytest.mark.parametrize(
    "where,function,response",
    [
        (10, lambda x: func.Max(x.city_id, "response"), 10),
        (10, lambda x: func.Min(x.city_id, "response"), 10),
        (10, lambda x: func.Sum(x.city_id, "response"), 10),
        (10, lambda x: func.Avg(x.city_id, "response"), 10),
        (10, lambda x: func.Abs(x.city_id, "response"), 10),
        (10, lambda x: func.Ceil(x.city_id, "response"), 10),
        (10, lambda x: func.Floor(x.city_id, "response"), 10),
        (10, lambda x: func.Round(x.city_id, "response"), 10),
        (10, lambda x: func.Pow(x.city_id, 2, "response"), 100),
        (10, lambda x: func.Sqrt(x.city_id, "response"), 3),
        (10, lambda x: func.Mod(x.city_id, 10, "response"), 0),
        (10, lambda x: func.Truncate(x.city_id, 0, "response"), 10),
    ],
)
def test_functions[T, TProp](sakila_engine: Engine, where, function: Callable[[T], tuple[TProp, ...]], response) -> None:  # noqa: F811
    class Response(BaseModel):
        response: int

    # fmt:off
    res = ( 
        ORM(Address, sakila_engine)
        .where(lambda x: x.city_id == where)
        .groupby(lambda x: x.city_id)
        .first(lambda x: function(x), flavour=Response)
    ) 
    # fmt:on
    assert res.response == response


def test_operator(sakila_engine: Engine):  # noqa: F811
    class Response(BaseModel):
        address: int
        city: int
        country: int
        truncate: int
        suma: int

    # fmt:off
    res = (
        ORM(Address, sakila_engine)
        .where(lambda x: x.address_id == 1)
        .order(lambda x: x.address_id,order_type='ASC')
        .first(lambda x: (
                Alias(x.address_id,"address"),
                Alias(x.City.city_id,"city"),
                Alias(x.City.Country.country_id,"country"),
                func.Truncate(x.address_id + x.City.city_id + x.City.Country.country_id, 2),
                Alias(x.address_id + x.City.city_id + x.City.Country.country_id, 'suma'),
            ), flavour=Response
        )
    )

    assert res.address,1
    assert res.city,300
    assert res.country,20
    assert res.truncate,res.address + res.city + res.country
    assert res.suma,res.truncate
    # fmt:on
    pass
