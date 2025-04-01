import sys
from pathlib import Path
from types import NoneType
import unittest
from datetime import datetime
from shapely import Point
from parameterized import parameterized
from typing import Any, NamedTuple, Type


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.caster import Caster, PLACEHOLDER
import ormlambda.databases as repository
from ormlambda import Column
from ormlambda import Table
from test.config import config_dict


class TestValues(Table):
    __table_name__ = "test_values"
    data_str: Column[str]
    data_int: Column[int]
    data_float: Column[float]
    data_Point: Column[Point]
    data_NoneType: Column[NoneType]
    data_datetime: Column[datetime]


table_obj = TestValues(
    data_str="value",
    data_int=20,
    data_float=20.001,
    data_Point=Point(5, -5),
    data_NoneType=None,
    data_datetime=datetime(1998, 12, 16, 10, 50, 59),
)

mysql_repo = repository.MySQLRepository(**config_dict)


class TestResultCast[TProp, TType](NamedTuple):
    wildcard_to_select: str
    wildcard_to_where: str
    wildcard_to_insert: str
    to_database: Any
    from_database: TProp
    value: TProp
    value_type: Type[TProp]
    type_to_cast: TType


RESULT_FOR_str = TestResultCast(
    wildcard_to_select=PLACEHOLDER,
    wildcard_to_where=PLACEHOLDER,
    wildcard_to_insert=PLACEHOLDER,
    to_database="value",
    from_database="value",
    value="value",
    value_type=str,
    type_to_cast=str,
)
RESULT_FOR_int = TestResultCast(
    wildcard_to_select=PLACEHOLDER,
    wildcard_to_where=PLACEHOLDER,
    wildcard_to_insert=PLACEHOLDER,
    to_database=20,
    from_database=20,
    value=20,
    value_type=int,
    type_to_cast=int,
)
RESULT_FOR_float = TestResultCast(
    wildcard_to_select=PLACEHOLDER,
    wildcard_to_where=PLACEHOLDER,
    wildcard_to_insert=PLACEHOLDER,
    to_database=20.001,
    from_database=20.001,
    value=20.001,
    value_type=float,
    type_to_cast=float,
)
RESULT_FOR_Point = TestResultCast(
    wildcard_to_select=f"ST_AsText({PLACEHOLDER})",
    wildcard_to_where=f"ST_AsText({PLACEHOLDER})",
    wildcard_to_insert=f"ST_GeomFromText({PLACEHOLDER})",
    to_database="POINT (5 -5)",
    from_database=Point(5, -5),
    value=Point(5, -5),
    value_type=Point,
    type_to_cast=Point,
)
RESULT_FOR_NoneType = TestResultCast(
    wildcard_to_select=PLACEHOLDER,
    wildcard_to_where=PLACEHOLDER,
    wildcard_to_insert=PLACEHOLDER,
    to_database=None,
    from_database=None,
    value=None,
    value_type=NoneType,
    type_to_cast=NoneType,
)
RESULT_FOR_datetime = TestResultCast(
    wildcard_to_select=PLACEHOLDER,
    wildcard_to_where=PLACEHOLDER,
    wildcard_to_insert=PLACEHOLDER,
    to_database=datetime(1998, 12, 16, 10, 50, 59),
    from_database=datetime(1998, 12, 16, 10, 50, 59),
    value=datetime(1998, 12, 16, 10, 50, 59),
    value_type=datetime,
    type_to_cast=datetime,
)


class TestResolverType(unittest.TestCase):
    @parameterized.expand(
        [
            (TestValues.data_Point, table_obj, RESULT_FOR_Point),
            (TestValues.data_str, table_obj, RESULT_FOR_str),
            (TestValues.data_int, table_obj, RESULT_FOR_int),
            (TestValues.data_float, table_obj, RESULT_FOR_float),
            (TestValues.data_NoneType, table_obj, RESULT_FOR_NoneType),
            (TestValues.data_datetime, table_obj, RESULT_FOR_datetime),
        ]
    )
    def test_for_column_with_column_obj[TProp](self, column: Column[TProp], table_obj: TestValues, result: TestResultCast) -> None:
        caster = Caster(mysql_repo)
        casted_data = caster.for_column(column, table_obj)
        self.assertEqual(casted_data.wildcard_to_select(), result.wildcard_to_select)
        self.assertEqual(casted_data.wildcard_to_where(), result.wildcard_to_where)
        self.assertEqual(casted_data.wildcard_to_insert(), result.wildcard_to_insert)
        self.assertEqual(casted_data.to_database, result.to_database)
        self.assertEqual(casted_data.from_database, result.from_database)
        self.assertEqual(casted_data.value, result.value)
        self.assertEqual(casted_data.value_type, result.value_type)
        self.assertEqual(casted_data.type_to_cast, result.type_to_cast)

    @parameterized.expand(
        [
            (table_obj.data_str, RESULT_FOR_str),
            (table_obj.data_int, RESULT_FOR_int),
            (table_obj.data_float, RESULT_FOR_float),
            (table_obj.data_Point, RESULT_FOR_Point),
            (table_obj.data_NoneType, RESULT_FOR_NoneType),
            (table_obj.data_datetime, RESULT_FOR_datetime),
        ]
    )
    def test_for_value[TProp](self, value: TProp, result: TestResultCast) -> None:
        caster = Caster(mysql_repo)
        casted_data = caster.for_value(value)
        self.assertEqual(casted_data.wildcard_to_select(), result.wildcard_to_select)
        self.assertEqual(casted_data.wildcard_to_where(), result.wildcard_to_where)
        self.assertEqual(casted_data.wildcard_to_insert(), result.wildcard_to_insert)
        self.assertEqual(casted_data.to_database, result.to_database)
        self.assertEqual(casted_data.from_database, result.from_database)
        self.assertEqual(casted_data.value, result.value)
        self.assertEqual(casted_data.value_type, result.value_type)
        self.assertEqual(casted_data.type_to_cast, result.type_to_cast)


if __name__ == "__main__":
    unittest.main()
