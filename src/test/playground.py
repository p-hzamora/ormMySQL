from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_sakila_engine
from ormlambda import ORM
from test.models import Address 


engine = create_sakila_engine()


def pagination(limit: int = 0, skip: int = 0) -> tuple:
    model = ORM(Address, engine)

    if limit:
        model.limit(limit)

    if skip:
        model.offset(skip)

    return model.select()


# for x in range(0, 100, 20):
#     data = pagination(x, x)

# fmt: off
res = (
    ORM(Address, engine)
    .where(lambda x: x.address_id >= 10)
    .where(lambda x: x.City.city_id > 4)
    .select()
)

res2 = (
    ORM(Address, engine)
    .where(lambda x: [
        x.address_id >= 10,
        x.City.city_id > 4,
        ]
    ) 
    .select()
)
# fmt: on
assert res== res2
