from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from pydantic import BaseModel
from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM


class TestConcat(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = create_sakila_engine()
        cls.tmodel = ORM(Address, cls.ddbb)

    def test_concat(self):
        class QueryResponse(BaseModel):
            address: str
            city: str
            concat: str

        concat = self.tmodel.where(Address.City.Country.country.regex(r"^Spain")).first(
            lambda x: (
                x.address,
                x.City.city,
                self.tmodel.concat(
                    (
                        "Address: ",
                        x.address,
                        " - city: ",
                        x.City.city,
                        " - country: ",
                        x.City.Country.country,
                    ),
                    alias="concat",
                ),
            ),
            flavour=QueryResponse,
        )

        res = QueryResponse(
            address="939 Probolinggo Loop",
            city="A Coruña (La Coruña)",
            concat="Address: 939 Probolinggo Loop - city: A Coruña (La Coruña) - country: Spain",
        )
        self.assertEqual(concat, res)

    def test_concat_without_lambda(self):
        concat = self.tmodel.where(Address.City.Country.country.regex(r"^Spain")).first(
            (
                Address.address,
                Address.City.city,
                self.tmodel.concat(
                    (
                        "Address: ",
                        Address.address,
                        " - city: ",
                        Address.City.city,
                        " - country: ",
                        Address.City.Country.country,
                    ),
                    alias="CONCAT",
                ),
            ),
            flavour=dict,
        )

        res = {
            "address_address": "939 Probolinggo Loop",
            "city_city": "A Coruña (La Coruña)",
            "CONCAT": "Address: 939 Probolinggo Loop - city: A Coruña (La Coruña) - country: Spain",
        }
        self.assertDictEqual(concat, res)


if __name__ == "__main__":
    unittest.main()
