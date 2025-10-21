from __future__ import annotations


from ormlambda import Count, IStatements
from test.models import Address  # noqa: E402

from pydantic import BaseModel


def test_groupby(amodel: IStatements[Address]) -> None:
    class Response(BaseModel):
        district: str
        count: int

    # fmt: off
    res = (
        amodel
        .groupby(lambda x: x.district)
        .order(lambda x: x.count, "DESC")
        .having(lambda x: x.count >= 5)
        .select(lambda x:
            (
                x.district,
                Count(x.address),
            ),
            flavour=Response,
        )
    )
    # fmt: on

    TOTAL_SUM = sum(x.count for x in res)

    class Response2(BaseModel):
        district: str
        address: str

    results = [r.district for r in res]
    # fmt: off
    res2 = (
        amodel
        .where(lambda x: x.district.contains(results))
        .order(lambda x:x.district, "DESC")
        .select(lambda x: 
                (
                    x.district,
                    x.address
                ),
                flavour=Response2)
    )
    # fmt: on
    EXPECTED = len(res2)
    assert TOTAL_SUM == EXPECTED
