from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM
from pydantic import BaseModel
from ormlambda import Min, Max


class MaxMinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_sakila_engine()
        cls.tmodel = ORM(Address, cls.ddbb)

    def test_max_and_min(self):
        # fmt: off
        res = (
            self.tmodel
            .where(lambda x: (
                x.address_id <= 200,
                x.address_id >= 100))
            .first(lambda x: (
                Max(x.address_id),
                Min(x.address_id),
                ),
                flavour=dict,
            )
        )
        # fmt: on

        self.assertEqual(res["max"], 200)
        self.assertEqual(res["min"], 100)

    def test_max_min_with_aliases(self):
        class MaxMinResponse(BaseModel):
            addressIdMax: int
            addressIdMin: int

        # fmt: off
        res = (
            self.tmodel
            .where(lambda x: (x.address_id <= 200, x.address_id >= 100))
            .first(lambda x: (
                Max(x.address_id, "addressIdMax"),
                Min(x.address_id, "addressIdMin"),
                ),
                flavour=MaxMinResponse,
            )
        )
        # fmt: off
        self.assertEqual(res.addressIdMax, 200)
        self.assertEqual(res.addressIdMin, 100)

    def test_max_with_lambda(self):
        res1 = self.tmodel.groupby(lambda x: x.address_id).max(lambda x: x.address_id)
        res2 = self.tmodel.groupby(lambda x: x.address_id).max(lambda x: x.address_id)

        self.assertEqual(res1, res2)

    def test_min_with_lambda(self):
        res1 = self.tmodel.groupby(lambda x: x.address_id).min(lambda x: x.address_id)
        res2 = self.tmodel.groupby(lambda x: x.address_id).min(lambda x: x.address_id)

        self.assertEqual(res1, res2)

    def test_sum_with_lambda(self):
        res1 = self.tmodel.groupby(lambda x: x.address_id).sum(lambda x: x.address_id)
        res2 = self.tmodel.groupby(lambda x: x.address_id).sum(lambda x: x.address_id)

        self.assertEqual(res1, res2)


if __name__ == "__main__":
    unittest.main()
