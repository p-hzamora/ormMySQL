from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from pydantic import BaseModel
from test.config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM, Column


class TestComplexQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = MySQLRepository(**config_dict)
        cls.tmodel = ORM(Address, cls.ddbb)

    def test_complex_1(self):
        class Response(BaseModel):
            pkUser: int
            pkCity: int
            count: int

        count = Column(str, column_name=self.tmodel.count(Address.address_id, None).query)
        res = (
            self.tmodel.where(Address.city_id >= 312)
            .having(count > 1)
            .groupby(Address.city_id)
            .select(
                (
                    self.tmodel.alias(Address.address_id, "pkUser"),
                    self.tmodel.alias(Address.city_id, "pkCity"),
                    self.tmodel.count(Address.address_id, "count"),
                ),
                flavour=Response,
            )
        )
        self.assertEqual(res, Response(pkUser=100, addressIdMax=200, addressIdMin=100))


if __name__ == "__main__":
    unittest.main()
