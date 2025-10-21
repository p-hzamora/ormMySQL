from __future__ import annotations

import pytest


from ormlambda import OrderType
from ormlambda import Table
from ormlambda import ORM
from ormlambda import Column
from ormlambda import IStatements

DB_NAME = "__test_ddbb__"


class OrderTest(Table):
    __table_name__ = "__test_ddbb__.order_table_test"
    pk: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    a: Column[int]
    b: Column[int]
    c: Column[int]


@pytest.fixture(scope="module", autouse=True)
def engine(engine_no_db, create_engine_for_db):
    engine_no_db.create_schema(DB_NAME, "replace")

    _engine = create_engine_for_db(DB_NAME)
    omodel = ORM(OrderTest, _engine)

    omodel.create_table()
    omodel.insert(
        (
            OrderTest(None, 1, 1, 1),
            OrderTest(None, 1, 2, 1),
            OrderTest(None, 1, 3, 2),
            OrderTest(None, 1, 3, 3),
            OrderTest(None, 1, 3, 4),
            OrderTest(None, 1, 4, 5),
            OrderTest(None, 2, 5, 6),
            OrderTest(None, 2, 6, 7),
            OrderTest(None, 2, 7, 8),
            OrderTest(None, 3, 8, 9),
        )
    )
    yield _engine

    engine_no_db.drop_schema(DB_NAME)


@pytest.fixture
def omodel(engine) -> IStatements[OrderTest]:
    model = ORM(OrderTest, engine)

    return model
    # model.delete()


def test_order(omodel: IStatements[OrderTest]):
    print(omodel)
    #fmt: off
    query = (
        omodel
        .order(lambda x: (x.a, x.b, x.c), [OrderType.ASC, OrderType.DESC, OrderType.ASC])
        .select(lambda x: 
            (
                x.a, 
                x.b, 
                x.c,
            ),
        flavour=tuple,
    )
    )
    #fmt: on

    tuple_ = (
        (1, 4, 5),
        (1, 3, 2),
        (1, 3, 3),
        (1, 3, 4),
        (1, 2, 1),
        (1, 1, 1),
        (2, 7, 8),
        (2, 6, 7),
        (2, 5, 6),
        (3, 8, 9),
    )
    assert tuple_ == query


def test_order_with_strings(omodel: IStatements[OrderTest]):
    query = omodel.order(lambda x: (x.a, x.b, x.c), ["ASC", "DESC", "ASC"]).select(
        lambda x: (x.a, x.b, x.c),
        flavour=tuple,
    )

    tuple_ = (
        (1, 4, 5),
        (1, 3, 2),
        (1, 3, 3),
        (1, 3, 4),
        (1, 2, 1),
        (1, 1, 1),
        (2, 7, 8),
        (2, 6, 7),
        (2, 5, 6),
        (3, 8, 9),
    )
    assert tuple_ == query


def test_order_with_strings_and_enums(omodel: IStatements[OrderTest]):
    query = omodel.order(lambda x: (x.a, x.b, x.c), ["ASC", OrderType.DESC, "ASC"]).select(
        lambda x: (x.a, x.b, x.c), 
        flavour=tuple,
    )

    tuple_ = (
        (1, 4, 5),
        (1, 3, 2),
        (1, 3, 3),
        (1, 3, 4),
        (1, 2, 1),
        (1, 1, 1),
        (2, 7, 8),
        (2, 6, 7),
        (2, 5, 6),
        (3, 8, 9),
    )
    assert tuple_ == query


def test_order_by_first_column(omodel: IStatements[OrderTest]):
    query = omodel.order(lambda x: x.a, OrderType.ASC).select(
        lambda x: (x.a, x.b, x.c),
        flavour=tuple,
    )

    tuple_ = (
        (1, 1, 1),
        (1, 2, 1),
        (1, 3, 2),
        (1, 3, 3),
        (1, 3, 4),
        (1, 4, 5),
        (2, 5, 6),
        (2, 6, 7),
        (2, 7, 8),
        (3, 8, 9),
    )
    assert tuple_ == query


def test_order_by_second_column(omodel: IStatements[OrderTest]):
    query = omodel.order(lambda x: x.b, OrderType.DESC).select(
        lambda x: (x.a, x.b, x.c),
        flavour=tuple,
    )

    tuple_ = (
        (3, 8, 9),
        (2, 7, 8),
        (2, 6, 7),
        (2, 5, 6),
        (1, 4, 5),
        (1, 3, 2),
        (1, 3, 3),
        (1, 3, 4),
        (1, 2, 1),
        (1, 1, 1),
    )
    assert tuple_ == query


def test_order_by_third_column(omodel: IStatements[OrderTest]):
    query = omodel.order(lambda x: x.c, OrderType.DESC).select(
        lambda x: (x.a, x.b, x.c),
        flavour=tuple,
    )

    tuple_ = (
        (3, 8, 9),
        (2, 7, 8),
        (2, 6, 7),
        (2, 5, 6),
        (1, 4, 5),
        (1, 3, 4),
        (1, 3, 3),
        (1, 3, 2),
        (1, 1, 1),
        (1, 2, 1),
    )
    assert tuple_ == query
