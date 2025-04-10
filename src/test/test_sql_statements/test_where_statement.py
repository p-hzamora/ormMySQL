from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from test.models import Address, City, Country  # noqa: F401
from ormlambda import ORM

import re


class RegexFilter:
    def __init__(self, pattern: str, value: str, *kwargs) -> None:
        self._compile: re.Pattern = re.compile(pattern, *kwargs)
        self._value: str = value


class TestWhereStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb = MySQLRepository(**config_dict)
        cls.tmodel = ORM(Address, cls.ddbb)

    def test_where(self):
        co = "Spain"
        select = (
            self.tmodel.offset(3)
            .where(Address.City.Country.country == co)
            .limit(2)
            .order(lambda x: x.City.city, "ASC")
            .select(
                lambda x: x.City.city,
                flavour=tuple,
            )
        )

        res = (
            ("Ourense (Orense)"),
            ("Santiago de Compostela"),
        )
        self.assertTupleEqual(select, res)

    def test_multiple_wheres_using_tables(self) -> None:
        city = "Ourense (Orense)"
        country = r"[sS]pain"

        result = self.tmodel.where(
            [
                Address.City.Country.country.regex(country),
                Address.City.city == city,
            ]
        ).select(
            (City.city, Country.country),
            flavour=dict,
        )

        self.assertEqual(len(result), 1)
        self.assertDictEqual(
            result[0],
            {
                "city_city": "Ourense (Orense)",
                "country_country": "Spain",
            },
        )

    def test_multiple_wheres_using_lambda(self) -> None:
        city = "Ourense (Orense)"
        country = r"[sS]pain"

        result = self.tmodel.where(
            lambda x: (
                x.City.Country.country.regex(country),
                x.City.city == city,
            )
        ).select(
            lambda x: (x.City.city, x.City.Country.country),
            flavour=dict,
        )

        self.assertEqual(len(result), 1)
        self.assertDictEqual(
            result[0],
            {
                "city_city": "Ourense (Orense)",
                "country_country": "Spain",
            },
        )


if __name__ == "__main__":
    unittest.main()
