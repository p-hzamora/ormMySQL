from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM, Alias


class TestAlias(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        engine = create_sakila_engine()
        cls.model = ORM(Address, engine)

    def test_alias_with_alias_attribute(self):
        res = self.model.where(lambda x: x.City.Country.country == "Spain").first(
            lambda x: (
                x.address_id,
                x.district,
                x.City.city,
                x.City.Country.country,
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
            lambda x: (
                Alias(x.address_id, "{column}"),
                Alias(x.district, "{column}"),
                Alias(x.City.city, "{column}"),
                Alias(x.City.Country.country, "{column}"),
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
