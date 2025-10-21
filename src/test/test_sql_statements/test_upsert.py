from typing import Callable, Generator
import pytest


from test.models import _TestTable
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine
from test.conftest import create_engine_for_db, engine_no_db  # noqa: F401

DDBB = "__test_ddbb__"


@pytest.fixture(scope="module")
def create_db(engine_no_db: Engine):  # noqa: F811
    engine_no_db.create_schema(DDBB, "replace")
    yield
    engine_no_db.drop_schema(DDBB)


@pytest.fixture(scope="function")
def tmodel(create_db, create_engine_for_db: Callable[[str], Engine]) -> Generator[IStatements[_TestTable], None, None]:  # noqa: F811
    model = ORM(_TestTable, create_engine_for_db(DDBB))
    model.create_table()
    yield model
    model.drop_table()


def create_instance_of_TestTable(number: int) -> list[_TestTable]:
    if number <= 0:
        number = 1
    return [_TestTable(*[x] * len(_TestTable.__annotations__)) for x in range(1, number + 1)]


def test_upsert(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(0)[0]
    tmodel.insert(instance)

    select_before_upsert = tmodel.where(lambda x: x.Col1 == 1).first()

    assert select_before_upsert == instance

    instance.Col10 = 999
    tmodel.upsert(instance)

    select_after_upsert = tmodel.where(lambda x: x.Col1 == 1).first()

    assert instance == select_after_upsert
    assert 999 == select_after_upsert.Col10
