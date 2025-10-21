from ormlambda import ORM, Count

from test.models import Address


def test_count_address_grouping_by_countries(sakila_engine) -> None:  # noqa: F811
    model = ORM(Address, sakila_engine)

    # fmt: off
    res= (
        model
            .order(lambda x: x.contar, order_type="DESC")
            .limit(10)
            .groupby(lambda x: (
                x.City.Country.country,
            ))
            .select(lambda x: (
                x.City.Country.country,
                Count(x.address_id,'contar')
            ),flavour=dict, 
        )
    )
    # fmt: on

    assert res == (
        {"country": "India", "contar": 60},
        {"country": "China", "contar": 53},
        {"country": "United States", "contar": 36},
        {"country": "Japan", "contar": 31},
        {"country": "Mexico", "contar": 30},
        {"country": "Russian Federation", "contar": 28},
        {"country": "Brazil", "contar": 28},
        {"country": "Philippines", "contar": 20},
        {"country": "Turkey", "contar": 15},
        {"country": "Indonesia", "contar": 14},
    )
