from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import datetime


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
        )

        self.model.insert(instance)
        select = self.model.select_one(lambda x: x.points, flavour=tuple)
        self.assertEqual(select, shp.Point(5, 5))

    def test_update_different_types(self):
        instance = TableType(
            pk=1,
            strings="strings",
            integers=10,
            floats=0.99,
            points=shp.Point(5, 5),
            datetimes=datetime(1998, 12, 16),
        )

        self.model.insert(instance)
        self.model.where(lambda x: x.pk == 1).update(
            {
                "integers": 99,
                TableType.strings: "new_strings",
                TableType.points: shp.Point(100, 100),
            }
        )

        select = self.model.where(lambda x: x.pk == 1).select_one()

        instance_after_update: TableType = TableType(
            pk=1,
            strings="new_strings",
            integers=99,
            floats=0.99,
            points=shp.Point(100, 100),
            datetimes=datetime(1998, 12, 16),
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


if __name__ == "__main__":
    unittest.main(failfast=True)
