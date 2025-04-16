from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_env_engine  # noqa: E402
from ormlambda import ORM  # noqa: E402
from ormlambda.common.errors import UnmatchedLambdaParameterError

from test.models import (
    TableType,
)  # noqa: E402


DDBBNAME = "__test_ddbb__"

MSSG_ERROR: str = "Unmatched number of parameters in lambda function with the number of tables: Expected 1 parameters but found ('x', 'y', 'z')."

class TestWorkingWithDifferentTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_env_engine()

    def setUp(self) -> None:
        self.ddbb.create_database(DDBBNAME, "replace")
        self.ddbb.database = DDBBNAME
        self.model = ORM(TableType, self.ddbb)
        self.model.create_table("replace")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_database(DDBBNAME)

    def test_UnmatchedLambdaParameterError_in_where(self):
        with self.assertRaises(UnmatchedLambdaParameterError) as err:
            self.model.where(lambda x, y, z: x.points == 2).select_one(lambda x: x.points, flavour=tuple)

        self.assertEqual(MSSG_ERROR, err.exception.__str__())

    def test_UnmatchedLambdaParameterError_in_select_one(self):
        with self.assertRaises(UnmatchedLambdaParameterError) as err:
            self.model.select_one(lambda x, y, z: x.points, flavour=tuple)

        self.assertEqual(MSSG_ERROR, err.exception.__str__())

    def test_UnmatchedLambdaParameterError_in_select(self):
        with self.assertRaises(UnmatchedLambdaParameterError) as err:
            self.model.select(lambda x, y, z: x.points, flavour=tuple)

        self.assertEqual(MSSG_ERROR, err.exception.__str__())


if __name__ == "__main__":
    unittest.main(failfast=True)
