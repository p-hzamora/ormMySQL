from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import datetime, date
import decimal


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from ormlambda import ORM

from test.models import (
    TableType,
)  # noqa: E402

import shapely as shp

DDBBNAME = "__test_ddbb__"


env_engine = create_env_engine()


class TestWorkingWithDifferentTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        env_engine.create_schema(DDBBNAME, "replace")
        cls.ddbb = create_engine_for_db(DDBBNAME)

        cls.model = ORM(TableType, cls.ddbb)
        cls.model.create_table("fail")

    def setUp(self) -> None:
        if self.model.count():
            self.model.delete()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_schema(DDBBNAME)

    def test_create_model_with_wrong_types(self):
        with self.assertRaises(ValueError):
            TableType(
                pk=1,
                strings=1,
                integers=10.00,
                floats=5,
            )

    def test_insert_different_types(self):
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

        self.model.insert(instance)
        select = self.model.select_one()
        self.assertEqual(select.pk, 1)
        self.assertEqual(select.strings, "strings")
        self.assertEqual(select.integers, 10)
        self.assertEqual(select.floats, 0.99)
        self.assertEqual(select.points, shp.Point(5, 5))
        self.assertEqual(select.datetimes, datetime(1998, 12, 16))
        self.assertEqual(select.dates, date(1998, 12, 16))
        self.assertEqual(select.decimals, decimal.Decimal("26.67"))
        self.assertEqual(select.jsons, {"new_value": 200, "errors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "is_valid": True})

    def test_update_different_types(self):
        instance = TableType(
            pk=1,
            strings="strings",
            integers=10,
            floats=0.99,
            points=shp.Point(5, 5),
            datetimes=datetime(1998, 12, 16),
            jsons={"new_value": 200, "errors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "is_valid": True},
        )

        self.model.insert(instance)
        self.model.where(lambda x: x.pk == 1).update(
            {
                "integers": 99,
                TableType.strings: "new_strings",
                TableType.points: shp.Point(100, 100),
                TableType.jsons: {"is_valid": False},
            },
        )

        select = self.model.where(lambda x: x.pk == 1).select_one()

        instance_after_update: TableType = TableType(
            pk=1,
            strings="new_strings",
            integers=99,
            floats=0.99,
            points=shp.Point(100, 100),
            datetimes=datetime(1998, 12, 16),
            jsons={"is_valid": False},
        )

        self.assertEqual(select, instance_after_update)

    def test_that_all_flavours_returns_the_same_data[T](self, flavour: T = None):
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
        self.model.insert(instance)
        select_None = tuple(self.model.first().to_dict().values())
        select_dict = tuple(self.model.first(flavour=dict).values())
        select_list = self.model.first(flavour=list)
        select_tuple = self.model.first(flavour=tuple)
        select_set = self.model.first(flavour=set)

        self.assertTupleEqual(select_None, EXPECTED)
        self.assertTupleEqual(select_dict, EXPECTED)
        self.assertListEqual(select_list, list(EXPECTED))
        self.assertTupleEqual(select_tuple, EXPECTED)
        self.assertSetEqual(select_set, set(EXPECTED))

    def test_passing_list_into_json_datatype(self):
        data_list = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Boston"},
        ]

        instance = TableType(pk=1, jsons=data_list)

        self.model.insert(instance)
        result = self.model.where(TableType.pk == 1).first()
        self.assertEqual(result.jsons, data_list)

    def test_passing_dict_into_json_datatype(self):
        data_list = {
            "name": "John",
            "age": 30,
            "city": "New York",
            "errors": [5, 5, 5, 5, 5],
        }

        instance = TableType(pk=1, jsons=data_list)
        self.model.insert(instance)

        new_data = data_list.copy()
        new_data["errors"] = [5, 1, 5, 5, 5]
        self.model.where(lambda x: x.pk == 1).update({TableType.jsons: new_data})

        result = self.model.where(TableType.pk == 1).first()
        self.assertEqual(result.jsons, new_data)

    def test_passing_nested_list_into_json_datatype(self):
        data_list = [{"name": "pablo", "errors": [{"1": "first", "2": "second", "3": "third"}]}]

        instance = TableType(pk=1, jsons=data_list)
        self.model.insert(instance)

        new_data = [{"name": "pablo", "errors": [{"1": [], "2": "second", "3": "third"}]}]

        self.model.where(TableType.pk == 1).update({TableType.jsons: new_data})
        result = self.model.where(TableType.pk == 1).first()
        self.assertEqual(result.jsons, new_data)


if __name__ == "__main__":
    unittest.main(failfast=True)
