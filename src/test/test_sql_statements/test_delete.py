from typing import Generator
import pytest


from test.models import _TestTable
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine

DDBB = "__test_ddbb__"


@pytest.fixture(scope="module", autouse=True)
def create_db(engine_no_db: Engine):  # noqa: F811
    engine_no_db.create_schema(DDBB, "replace")
    yield
    engine_no_db.drop_schema(DDBB)


@pytest.fixture(scope="function")
def tmodel(create_engine_for_db) -> Generator[IStatements[_TestTable], None, None]:  # noqa: F811
    model = ORM(_TestTable, create_engine_for_db(DDBB))
    model.create_table()
    yield model
    model.drop_table()


def create_instance_of_TestTable(number: int) -> list[_TestTable]:
    if number <= 0:
        number = 1
    return [_TestTable(*[x] * len(_TestTable.__annotations__)) for x in range(1, number + 1)]


def test_delete_one_element(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    result = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert result == (1, 2, 3, 4, 5)

    tmodel.where(lambda x: x.Col1 == 3).delete()
    result = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert result == (1, 2, 4, 5)


def test_delete_a_couple_of_elements(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    result = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert result == (1, 2, 3, 4, 5)

    # fmt:off
    (
        tmodel
        .where(lambda x: x.Col1 == 2)
        .where(lambda x: x.Col1 == 3)
        .where(lambda x: x.Col1 == 4)
        .delete()
    )
    # fmt:on
    result = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert result == (1, 5)


def test_delete(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    tmodel.where(lambda x: x.Col1 == 2).delete()
    select_all = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert (1, 3, 4, 5) == select_all


def test_delete_passing_instance(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    tmodel.delete(_TestTable(2))
    select_all = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert (1, 3, 4, 5) == select_all


def test_delete_passing_list_of_instance(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    tmodel.delete(
        [
            _TestTable(2),
            _TestTable(3),
            _TestTable(4),
        ]
    )
    select_all = tmodel.select(lambda x: x.Col1, flavour=tuple)
    assert (1, 5) == select_all


def test_delete_all(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    assert tmodel.count() == 5

    tmodel.delete()
    assert tmodel.count() == 0
