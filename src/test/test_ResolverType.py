import sys
from pathlib import Path
from types import NoneType
import typing as tp
import unittest
from datetime import datetime
from shapely import Point

from parameterized import parameterized


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())


from ormlambda.databases.my_sql.caster import MySQLReadCastBase, MySQLWriteCastBase
from models import Country
from ormlambda import Table, Column


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


class TestResolverType(unittest.TestCase):
    @parameterized.expand(
        [
            ("value", "'value'"),
            (20, "20"),
            (20.001, "20.001"),
            (Point(5, -5), "ST_GeomFromText('POINT (5 -5)')"),
            (None, "NULL"),
            (datetime(1998, 12, 16, 10, 50, 59), "'1998-12-16 10:50:59'"),
            (Country.country, "country"),
        ]
    )
    def test_resolve_MySQLWriteCastBase(self, object_: tp.Any, result: str) -> tp.Any:
        resolver = MySQLWriteCastBase().resolve(object_)
        self.assertEqual(resolver, result)

    @parameterized.expand(
        [
            (table_obj.data_str, "value"),
            (table_obj.data_int, 20),
            (table_obj.data_float, 20.001),
            (table_obj.data_Point, Point(5, -5)),
            (table_obj.data_NoneType, None),
            (table_obj.data_datetime, datetime(1998, 12, 16, 10, 50, 59)),
        ]
    )
    def test_resolve_MySQLReadCastBase(self, column: Column, result: tp.Any) -> tp.Any:
        resolver = MySQLReadCastBase().resolve(column)
        self.assertEqual(resolver, result)


if __name__ == "__main__":
    unittest.main()
