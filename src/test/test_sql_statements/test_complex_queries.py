from __future__ import annotations
from typing import Optional
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from pydantic import BaseModel
from test.config import create_sakila_engine  # noqa: E402
from test.models import Address, City  # noqa: F401
from ormlambda import ORM, Column, OrderType, JoinType

engine = create_sakila_engine()


class Response(BaseModel):
    country: str
    sumCities: int


class TestComplexQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amodel = ORM(Address, engine)
        cls.cmodel = ORM(City, engine)

    def query(self, char_to_filter: str, limit: Optional[int] = None, offset: int = 0) -> tuple[Response, ...] | Response:
        response = self.cmodel.order(Column(column_name="sumCities"), "DESC").where([City.Country.country.like(f"%{char_to_filter}%")]).groupby(City.Country.country)

        if limit:
            response.limit(limit)

        if offset:
            response.offset(offset)

        res = response.select(
            (
                City.Country.country,
                self.cmodel.count(City, "sumCities"),
            ),
            flavour=Response,
        )
        return res[0] if len(res) == 1 else res

    def test_complex_1(self):
        class Response(BaseModel):
            pkCity: int
            count: int

        res = (
            self.amodel.where(Address.city_id >= 312)
            .having(Column(column_name="count") > 1)
            .groupby(Address.city_id)
            .select(
                (
                    self.amodel.alias(Address.city_id, "pkCity"),
                    self.amodel.count(Address.address_id, "count"),
                ),
                flavour=Response,
            )
        )
        RESULT = (
            Response(pkCity=312, count=2),
            Response(pkCity=576, count=2),
        )
        self.assertTupleEqual(res, RESULT)

    def test_extract_countries_with_white_space_in_the_name(self):
        res = self.query("spain")
        self.assertEqual(res, Response(country="Spain", sumCities=5))

    def test_dicctioanry_of_countries_with_commans_dots_and_white_spaces(self):
        result = {}

        for char in " ", ".", ",":
            q = self.query(char, limit=1)
            result[char] = q

        EXPECTED = {
            " ": Response(country="United States", sumCities=35),
            ".": Response(country="Virgin Islands, U.S.", sumCities=1),
            ",": Response(country="Congo, The Democratic Republic of the", sumCities=2),
        }
        self.assertEqual(result, EXPECTED)

    def test_get_country_with_more_address_registered(self):
        class Response(BaseModel):
            countryName: str
            contar: int

        res = (
            self.amodel.order("contar", OrderType.DESC)
            .groupby(Address.City.Country.country)
            .first(
                (
                    self.amodel.alias(Address.City.Country.country, "countryName"),
                    self.amodel.count(alias="contar"),
                ),
                flavour=Response,
                by=JoinType.LEFT_EXCLUSIVE,
            )
        )

        EXPECTED = Response(countryName="India", contar=60)
        self.assertEqual(res, EXPECTED)


if __name__ == "__main__":
    unittest.main()
