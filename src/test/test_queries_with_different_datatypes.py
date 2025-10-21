from __future__ import annotations
from datetime import datetime, date
import decimal
import pytest
from typing import Callable, Generator

from ormlambda import ORM, Engine, IStatements

from test.models import (
    TableType,
)  # noqa: E402

import shapely as shp

DB_NAME = "__test_ddbb__"


@pytest.fixture(scope="module", autouse=True)  # noqa: F821
def engine(engine_no_db: Engine, create_engine_for_db: Callable[[str], Engine]) -> Generator[Engine, None, None]:
    engine_no_db.create_schema(DB_NAME, "replace")
    engine = create_engine_for_db(DB_NAME)

    model = ORM(TableType, engine)
    model.create_table("fail")

    yield engine

    engine.drop_schema(DB_NAME)


@pytest.fixture
def model(engine: Engine):
    model = ORM(TableType, engine)

    if model.count():
        model.delete()

    return model


def test_create_model_with_wrong_types():
    with pytest.raises(ValueError):
        TableType(
            pk=1,
            strings=1,
            integers=10.00,
            floats=5,
        )


def test_insert_different_types(model: IStatements[TableType]):
    instance = TableType(
        pk=1,
        strings="strings",
        integers=10,
        floats=0.99,
        points=shp.Point(5, 5),
        datetimes=datetime(1998, 12, 16),
        dates=date(1998, 12, 16),
        decimals=decimal.Decimal("26.67"),
        jsons={"new_value": 200, "errors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "is_valid": True},
    )

    model.insert(instance)
    select = model.select_one()
    assert select.pk == 1
    assert select.strings == "strings"
    assert select.integers == 10
    assert select.floats == 0.99
    assert select.points == shp.Point(5, 5)
    assert select.datetimes == datetime(1998, 12, 16)
    assert select.dates == date(1998, 12, 16)
    assert select.decimals == decimal.Decimal("26.67")
    assert select.jsons == {"new_value": 200, "errors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "is_valid": True}


def test_update_different_types(model: IStatements[TableType]):
    instance = TableType(
        pk=1,
        strings="strings",
        integers=10,
        floats=0.99,
        points=shp.Point(5, 5),
        datetimes=datetime(1998, 12, 16),
        jsons={"new_value": 200, "errors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "is_valid": True},
    )

    model.insert(instance)
    model.where(lambda x: x.pk == 1).update(
        {
            "integers": 99,
            TableType.strings: "new_strings",
            TableType.points: shp.Point(100, 100),
            TableType.jsons: {"is_valid": False},
        },
    )

    select = model.where(lambda x: x.pk == 1).select_one()

    instance_after_update: TableType = TableType(
        pk=1,
        strings="new_strings",
        integers=99,
        floats=0.99,
        points=shp.Point(100, 100),
        datetimes=datetime(1998, 12, 16),
        jsons={"is_valid": False},
    )

    assert select == instance_after_update


def test_that_all_flavours_returns_the_same_data[T](model:IStatements[TableType]):
    """
    This method ensures that all casters are working as expected using different flavours tags
    - flavour=dict
    - flavour=tuple
    - flavour=list
    - flavour=CustomClass

    """
    instance = TableType(
        pk=1,
        strings="strings",
        integers=10,
        floats=0.99,
        points=shp.Point(5, 5),
        datetimes=datetime(1998, 12, 16),
    )

    EXPECTED = tuple(instance.to_dict().values())
    model.insert(instance)
    select_None = tuple(model.first().to_dict().values())
    select_dict = tuple(model.first(flavour=dict).values())
    select_list = model.first(flavour=list)
    select_tuple = model.first(flavour=tuple)
    select_set = model.first(flavour=set)

    assert select_None == EXPECTED
    assert select_dict == EXPECTED
    assert select_list == list(EXPECTED)
    assert select_tuple == EXPECTED
    assert select_set == set(EXPECTED)


def test_passing_list_into_json_datatype(model: IStatements[TableType]):
    data_list = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "Boston"},
    ]

    instance = TableType(pk=1, jsons=data_list)

    model.insert(instance)
    result = model.where(lambda x: x.pk == 1).first()
    assert result.jsons == data_list


def test_passing_dict_into_json_datatype(model: IStatements[TableType]):
    data_list = {
        "name": "John",
        "age": 30,
        "city": "New York",
        "errors": [5, 5, 5, 5, 5],
    }

    instance = TableType(pk=1, jsons=data_list)
    model.insert(instance)

    new_data = data_list.copy()
    new_data["errors"] = [5, 1, 5, 5, 5]
    model.where(lambda x: x.pk == 1).update({TableType.jsons: new_data})

    result = model.where(lambda x: x.pk == 1).first()
    assert result.jsons == new_data


def test_passing_nested_list_into_json_datatype(model: IStatements[TableType]):
    data_list = [{"name": "pablo", "errors": [{"1": "first", "2": "second", "3": "third"}]}]

    instance = TableType(pk=1, jsons=data_list)
    model.insert(instance)

    new_data = [{"name": "pablo", "errors": [{"1": [], "2": "second", "3": "third"}]}]

    model.where(lambda x: x.pk == 1).update({TableType.jsons: new_data})
    result = model.where(lambda x: x.pk == 1).first()
    assert result.jsons == new_data
