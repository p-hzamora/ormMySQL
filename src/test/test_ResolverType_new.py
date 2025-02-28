import sys
from pathlib import Path
from types import NoneType
from typing import Literal
import unittest
from datetime import datetime
from shapely import Point
from parameterized import parameterized


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.caster import Caster
from ormlambda.databases import repository as repository
from ormlambda import Column
from ormlambda import Table
import config


class TestValues(Table):
    __table_name__ = "test_values"
    data_str: str
    data_int: int
    data_float: float
    data_Point: Point
    data_NoneType: NoneType
    data_datetime: datetime


table_obj = TestValues(
    data_str="value",
    data_int=20,
    data_float=20.001,
    data_Point=Point(5, -5),
    data_NoneType=None,
    data_datetime=datetime(1998, 12, 16, 10, 50, 59),
)

mysql_repo = repository.MySQLRepository(**config.config_dict)

type TypeCastAttr = Literal[
    "from_database",
    "wildcard",
    "to_query",
]


class TestResolverType(unittest.TestCase):
    @parameterized.expand(
        [
            (
                TestValues.data_str,
                table_obj,
                {"from_database": "value", "wildcard": "%s", "to_query": "value"},
            ),
            (
                TestValues.data_str,
                table_obj,
                {
                    "from_database": "value",
                    "wildcard": "%s",
                    "to_query": "value",
                },
            ),
            (
                TestValues.data_int,
                table_obj,
                {
                    "from_database": 20,
                    "wildcard": "%s",
                    "to_query": "20",
                },
            ),
            (
                TestValues.data_float,
                table_obj,
                {
                    "from_database": 20.001,
                    "wildcard": "%s",
                    "to_query": "20.001",
                },
            ),
            (
                TestValues.data_Point,
                table_obj,
                {
                    "from_database": Point(5, -5),
                    "wildcard": "ST_GeomFromText(%s)",
                    "to_query": "POINT (5 -5)",
                },
            ),
            (
                TestValues.data_NoneType,
                table_obj,
                {
                    "from_database": None,
                    "wildcard": "%s",
                    "to_query": "NULL",
                },
            ),
            (
                TestValues.data_datetime,
                table_obj,
                {
                    "from_database": datetime(1998, 12, 16, 10, 50, 59),
                    "wildcard": "%s",
                    "to_query": datetime(1998, 12, 16, 10, 50, 59),
                },
            ),
        ]
    )
    def test_for_column_with_column_obj[TProp](self, column: Column[TProp], table_obj: TestValues, results: dict[TypeCastAttr, TProp | str]) -> None:
        caster = Caster(mysql_repo, table_obj)
        for attr, result in results.items():
            casted_data = caster.for_column(column)
            self.assertEqual(casted_data[attr], result)

    def test_for_column_with_lambda_str(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_str)
        self.assertEqual(casted_data.from_database, "value")
        self.assertEqual(casted_data.wildcard, "%s")
        self.assertEqual(casted_data.to_query, "value")

    def test_for_column_with_lambda_int(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_int)
        self.assertEqual(casted_data.from_database, 20)
        self.assertEqual(casted_data.wildcard, "%s")
        self.assertEqual(casted_data.to_query, "20")

    def test_for_column_with_lambda_float(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_float)
        self.assertEqual(casted_data.from_database, 20.001)
        self.assertEqual(casted_data.wildcard, "%s")
        self.assertEqual(casted_data.to_query, "20.001")

    def test_for_column_with_lambda_Point(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_Point)
        self.assertEqual(casted_data.from_database, Point(5, -5))
        self.assertEqual(casted_data.wildcard, "ST_GeomFromText(%s)")
        self.assertEqual(casted_data.to_query, "POINT (5 -5)")

    def test_for_column_with_lambda_NoneType(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_NoneType)
        self.assertEqual(casted_data.from_database, None)
        self.assertEqual(casted_data.wildcard, "%s")
        self.assertEqual(casted_data.to_query, "NULL")

    def test_for_column_with_lambda_datetime(self) -> None:
        caster = Caster(mysql_repo, table_obj)
        casted_data = caster.for_column(lambda x: x.data_datetime)
        self.assertEqual(casted_data.from_database, datetime(1998, 12, 16, 10, 50, 59))
        self.assertEqual(casted_data.wildcard, "%s")
        self.assertEqual(casted_data.to_query, datetime(1998, 12, 16, 10, 50, 59))

    def test_for_value_without_passing_instance(self) -> None:
        POINT = Point(1, -1) 
        BYTE_POINT = POINT.wkb
        caster = Caster(mysql_repo)
        casted_value = caster.for_value(BYTE_POINT,forced_type=Point)
        self.assertEqual(casted_value.from_database, POINT)


if __name__ == "__main__":
    unittest.main()
