
import pytest
from types import NoneType
from datetime import datetime
from shapely import Point
from typing import Any, NamedTuple, Type



from ormlambda.caster import Caster
from ormlambda import Column, Table
from ormlambda.dialects import mysql


DIALECT = mysql.dialect


class ValueTest(Table):
    __table_name__ = "test_values"
    data_str: Column[str]
    data_int: Column[int]
    data_float: Column[float]
    data_Point: Column[Point]
    data_NoneType: Column[NoneType]
    data_datetime: Column[datetime]


table_obj = ValueTest(
    data_str="value",
    data_int=20,
    data_float=20.001,
    data_Point=Point(5, -5),
    data_NoneType=None,
    data_datetime=datetime(1998, 12, 16, 10, 50, 59),
)


class ResultCastTest[TProp, TType](NamedTuple):
    wildcard_to_select: str
    wildcard_to_where: str
    wildcard_to_insert: str
    to_database: Any
    from_database: TProp
    value: TProp
    value_type: Type[TProp]
    type_to_cast: TType


RESULT_FOR_str = ResultCastTest(
    wildcard_to_select=Caster.PLACEHOLDER,
    wildcard_to_where=Caster.PLACEHOLDER,
    wildcard_to_insert=Caster.PLACEHOLDER,
    to_database="value",
    from_database="value",
    value="value",
    value_type=str,
    type_to_cast=str,
)
RESULT_FOR_int = ResultCastTest(
    wildcard_to_select=Caster.PLACEHOLDER,
    wildcard_to_where=Caster.PLACEHOLDER,
    wildcard_to_insert=Caster.PLACEHOLDER,
    to_database=20,
    from_database=20,
    value=20,
    value_type=int,
    type_to_cast=int,
)
RESULT_FOR_float = ResultCastTest(
    wildcard_to_select=Caster.PLACEHOLDER,
    wildcard_to_where=Caster.PLACEHOLDER,
    wildcard_to_insert=Caster.PLACEHOLDER,
    to_database=20.001,
    from_database=20.001,
    value=20.001,
    value_type=float,
    type_to_cast=float,
)
RESULT_FOR_Point = ResultCastTest(
    wildcard_to_select=f"ST_AsText({Caster.PLACEHOLDER})",
    wildcard_to_where=f"ST_AsText({Caster.PLACEHOLDER})",
    wildcard_to_insert=f"ST_GeomFromText({Caster.PLACEHOLDER})",
    to_database="POINT (5 -5)",
    from_database=Point(5, -5),
    value=Point(5, -5),
    value_type=Point,
    type_to_cast=Point,
)
RESULT_FOR_NoneType = ResultCastTest(
    wildcard_to_select=Caster.PLACEHOLDER,
    wildcard_to_where=Caster.PLACEHOLDER,
    wildcard_to_insert=Caster.PLACEHOLDER,
    to_database=None,
    from_database=None,
    value=None,
    value_type=NoneType,
    type_to_cast=NoneType,
)
RESULT_FOR_datetime = ResultCastTest(
    wildcard_to_select=Caster.PLACEHOLDER,
    wildcard_to_where=Caster.PLACEHOLDER,
    wildcard_to_insert=Caster.PLACEHOLDER,
    to_database=datetime(1998, 12, 16, 10, 50, 59),
    from_database=datetime(1998, 12, 16, 10, 50, 59),
    value=datetime(1998, 12, 16, 10, 50, 59),
    value_type=datetime,
    type_to_cast=datetime,
)


@pytest.mark.parametrize(
    "column,table_obj,result",
    [
        (ValueTest.data_Point, table_obj, RESULT_FOR_Point),
        (ValueTest.data_str, table_obj, RESULT_FOR_str),
        (ValueTest.data_int, table_obj, RESULT_FOR_int),
        (ValueTest.data_float, table_obj, RESULT_FOR_float),
        (ValueTest.data_NoneType, table_obj, RESULT_FOR_NoneType),
        (ValueTest.data_datetime, table_obj, RESULT_FOR_datetime),
    ],
)
def test_for_column_with_column_obj[TProp](column: Column[TProp], table_obj: ValueTest, result: ResultCastTest) -> None:
    caster = DIALECT().caster()
    casted_data = caster.for_column(column, table_obj)
    assert casted_data.wildcard_to_select() == result.wildcard_to_select
    assert casted_data.wildcard_to_where() == result.wildcard_to_where
    assert casted_data.wildcard_to_insert() == result.wildcard_to_insert
    assert casted_data.to_database == result.to_database
    assert casted_data.from_database == result.from_database
    assert casted_data.value == result.value
    assert casted_data.value_type == result.value_type
    assert casted_data.type_to_cast == result.type_to_cast


@pytest.mark.parametrize(
    "value,result",
    [
        (table_obj.data_str, RESULT_FOR_str),
        (table_obj.data_int, RESULT_FOR_int),
        (table_obj.data_float, RESULT_FOR_float),
        (table_obj.data_Point, RESULT_FOR_Point),
        (table_obj.data_NoneType, RESULT_FOR_NoneType),
        (table_obj.data_datetime, RESULT_FOR_datetime),
    ],
)
def test_for_value[TProp](value: TProp, result: ResultCastTest) -> None:
    caster = DIALECT().caster()
    casted_data = caster.for_value(value)
    assert casted_data.wildcard_to_select() == result.wildcard_to_select
    assert casted_data.wildcard_to_where() == result.wildcard_to_where
    assert casted_data.wildcard_to_insert() == result.wildcard_to_insert
    assert casted_data.to_database == result.to_database
    assert casted_data.from_database == result.from_database
    assert casted_data.value == result.value
    assert casted_data.value_type == result.value_type
    assert casted_data.type_to_cast == result.type_to_cast
