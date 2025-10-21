import random
from typing import Annotated, Generator

import pytest


from ormlambda import Table, Column, ORM, PrimaryKey, create_engine, IStatements, Engine
from test.conftest import DB_PASSWORD, DB_USERNAME

DB_NAME = "__ddbb_test__"


class TableCount(Table):
    __table_name__ = "table_count"
    pos: Annotated[Column[int], PrimaryKey()]
    a: Column[int]
    b: Column[int]
    c: Column[int]


@pytest.fixture(scope="module", autouse=True)
def engine(engine_no_db: Engine):
    engine_no_db.create_schema(DB_NAME, "replace")

    new_engine = create_engine(f"mysql://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/{DB_NAME}?pool_size=3")
    model = ORM(TableCount, new_engine)

    model.create_table()
    yield new_engine

    new_engine.drop_schema(DB_NAME)


@pytest.fixture
def model(engine) -> Generator[IStatements[TableCount], None, None]:
    model = ORM(TableCount, engine)

    yield model
    model.delete()


def TableCount_generator(n: int) -> list[TableCount]:
    if not n > 0:
        raise ValueError(f"'n' must not be less than '0'. You passed '{n}'")

    insert_values: list[TableCount] = []
    for x in range(0, n):
        rnd = lambda: random.randint(0, 1_000_000)  # noqa: E731
        insert_values.append(TableCount(x, rnd(), rnd(), rnd()))
    return insert_values


def test_count_all_rows(model: IStatements[TableCount]):
    n_before_insert = model.count()

    model.insert(TableCount_generator(4))
    n_after_insert = model.count()

    model.delete()
    n_after_delete = model.count()

    assert n_before_insert == 0
    assert n_after_insert == 4
    assert n_after_delete == n_before_insert


def test_count_when_filtering(model: IStatements[TableCount]):
    model.insert(TableCount_generator(100))

    n_select = model.where(lambda x: (x.pos <= 70) & (x.pos >= 50)).count()

    assert n_select == 21


def test_count_when_filtering_using_list(model: IStatements[TableCount]):
    model.insert(TableCount_generator(100))

    n_select = model.where(
        lambda x: [
            x.pos <= 70,
            x.pos >= 50,
        ]
    ).count()

    assert n_select == 21


def test_count_excluding_NULL_for_column(model: IStatements[TableCount]):
    all_rows = TableCount_generator(100)

    for x in range(100):
        if x < 10:
            all_rows[x].a = None

    model.insert(all_rows)

    rows_different_none = model.count(lambda x: x.a)

    assert rows_different_none == 90


def test_clean_query_list(model: IStatements[TableCount]):
    insert: list[TableCount] = []

    for x in range(1, 101):
        if x < 21:
            table_count: TableCount = TableCount(x, 20, x, x)
        elif 21 <= x < 81:
            table_count: TableCount = TableCount(x, 80, x, x)
        elif 81 <= x < 101:
            table_count: TableCount = TableCount(x, 100, x, x)

        insert.append(table_count)

    model.insert(insert)
    n = model.count()
    n_20 = model.where(lambda x: x.a == 20).count()
    n_80 = model.where(lambda x: x.a == 80).count()
    n_100 = model.where(lambda x: x.a == 100).count()

    assert n == 100
    assert n_20 == 20
    assert n_80 == 60
    assert n_100 == 20
