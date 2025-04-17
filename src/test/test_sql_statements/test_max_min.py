from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM
from pydantic import BaseModel


class MaxMinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_sakila_engine()
        cls.tmodel = ORM(Address, cls.ddbb)

    def test_max_and_min(self):
        res = self.tmodel.where((Address.address_id <= 200, Address.address_id >= 100)).first(
            (
                self.tmodel.max(Address.address_id),
                self.tmodel.min(Address.address_id),
            ),
            flavour=dict,
        )

        self.assertEqual(res["max"], 200)
        self.assertEqual(res["min"], 100)

    def test_max_min_with_aliases(self):
        class MaxMinResponse(BaseModel):
            addressIdMax: int
            addressIdMin: int

        res = self.tmodel.where((Address.address_id <= 200, Address.address_id >= 100)).first(
            selector=(
                self.tmodel.max(Address.address_id, "addressIdMax"),
                self.tmodel.min(Address.address_id, "addressIdMin"),
            ),
            flavour=MaxMinResponse,
        )
        self.assertEqual(res.addressIdMax, 200)
        self.assertEqual(res.addressIdMin, 100)


    def test_max_with_lambda(self):
        res1 = self.tmodel.groupby(Address.address_id).first(self.tmodel.max(Address.address_id), flavour=dict)
        res2 = self.tmodel.groupby(Address.address_id).first(self.tmodel.max(lambda x: x.address_id), flavour=dict)

        self.assertDictEqual(res1, res2)

    def test_min_with_lambda(self):
        res1 = self.tmodel.groupby(Address.address_id).first(self.tmodel.min(Address.address_id), flavour=dict)
        res2 = self.tmodel.groupby(Address.address_id).first(self.tmodel.min(lambda x: x.address_id), flavour=dict)

        self.assertDictEqual(res1, res2)

    def test_sum_with_lambda(self):
        res1 = self.tmodel.groupby(Address.address_id).first(self.tmodel.sum(Address.address_id), flavour=dict)
        res2 = self.tmodel.groupby(Address.address_id).first(self.tmodel.sum(lambda x: x.address_id), flavour=dict)

        self.assertDictEqual(res1, res2)

if __name__ == "__main__":
    unittest.main()
