from typing import Callable, Generator
import pytest


from test.models import _TestTable
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine
from test.conftest import create_engine_for_db, engine_no_db  # noqa: F401

DDBB = "__test_ddbb__"


@pytest.fixture(scope="module", autouse=True)
def create_db(engine_no_db: Engine):  # noqa: F811
    engine_no_db.create_schema(DDBB, "replace")
    yield
    engine_no_db.drop_schema(DDBB)


@pytest.fixture(scope="function")
def tmodel(create_engine_for_db: Callable[[str], Engine]) -> Generator[IStatements[_TestTable], None, None]:  # noqa: F811
    model = ORM(_TestTable, create_engine_for_db(DDBB))
    model.create_table()
    yield model
    model.drop_table()


def create_instance_of_TestTable(number: int) -> list[_TestTable]:
    if number <= 0:
        number = 1
    return [_TestTable(*[x] * len(_TestTable.__annotations__)) for x in range(1, number + 1)]


def test_update_with_column_as_keys(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    tmodel.where(lambda x: x.Col1 == 3).update(
        {
            _TestTable.Col2: 2,
            _TestTable.Col5: 5,
            _TestTable.Col13: 13,
        }
    )
    theorical_result = instance[2]
    theorical_result.Col2 = 2
    theorical_result.Col5 = 5
    theorical_result.Col13 = 13

    result = tmodel.where(lambda x: x.Col1 == 3).select_one()
    assert result == theorical_result


def test_update_Col2(tmodel: IStatements[_TestTable]):
    instance = create_instance_of_TestTable(5)
    tmodel.insert(instance)

    OTHER_NUMBER = 2000

    tmodel.where(lambda x: x.Col1 == 3).update({_TestTable.Col2: OTHER_NUMBER})
    theorical_result = _TestTable(**instance[2].to_dict())
    theorical_result.Col2 = OTHER_NUMBER

    result = tmodel.select()
    assert result[0] == instance[0]
    assert result[1] == instance[1]
    assert result[2] == theorical_result != instance[2]
    assert result[3] == instance[3]
    assert result[4] == instance[4]
