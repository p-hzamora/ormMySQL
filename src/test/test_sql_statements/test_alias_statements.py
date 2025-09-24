from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM


class TestAlias(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        engine = create_sakila_engine()
        cls.model = ORM(Address, engine)

    def test_alias_with_alias_attribute(self):
        res = self.model.where(lambda x: x.City.Country.country == "Spain").first(
            (
                Address.address_id,
                Address.district,
                Address.City.city,
                Address.City.Country.country,
            ),
            flavour=dict,
            alias="{column}",
        )
        EXPECTED = {
            "address_id": 56,
            "district": "Galicia",
            "city": "A Coruña (La Coruña)",
            "country": "Spain",
        }
        self.assertDictEqual(res, EXPECTED)

    def test_alias_passing_alias_method(self):
        res = self.model.where(lambda x: x.City.Country.country == "Spain").first(
            (
                self.model.alias(Address.address_id, "{column}"),
                self.model.alias(Address.district, "{column}"),
                self.model.alias(Address.City.city, "{column}"),
                self.model.alias(Address.City.Country.country, "{column}"),
            ),
            flavour=dict,
        )
        EXPECTED = {
            "address_id": 56,
            "district": "Galicia",
            "city": "A Coruña (La Coruña)",
            "country": "Spain",
        }
        self.assertDictEqual(res, EXPECTED)


if __name__ == "__main__":
    unittest.main()
