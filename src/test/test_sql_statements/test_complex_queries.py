from __future__ import annotations
from typing import Optional
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from pydantic import BaseModel
from test.config import create_sakila_engine  # noqa: E402
from test.models import Address  # noqa: F401
from ormlambda import ORM, Column, OrderType

engine = create_sakila_engine()


class TestComplexQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmodel = ORM(Address, engine)

    def test_complex_1(self):
        class Response(BaseModel):
            pkCity: int
            count: int

        count = Column(column_name="count")
        res = (
            self.tmodel.where(Address.city_id >= 312)
            .having(count > 1)
            .groupby(Address.city_id)
            .select(
                (
                    self.tmodel.alias(Address.city_id, "pkCity"),
                    self.tmodel.count(Address.address_id, "count"),
                ),
                flavour=Response,
            )
        )
        RESULT = (
            Response(pkCity=312, count=2),
            Response(pkCity=576, count=2),
        )
        self.assertTupleEqual(res, RESULT)

    def test_AAextract_countries_with_white_space_in_the_name(self):
        class Response(BaseModel):
            country: str
            sumAddress: int
            sumCities: int
            query: Optional[str] = None

        def query(char_to_filter: str, limit: Optional[int] = None, offset: int = 0) -> Response:
            response = (
                self.tmodel.order(Column(column_name="sumAddress"), "DESC")
                .where(
                    [
                        Address.City.Country.country.like(f"%{char_to_filter}%"),
                    ]
                )
                .groupby(Address.City.Country.country)
            )

            if limit:
                response.limit(limit)

            if offset:
                response.offset(offset)

            _query = response.select(
                (
                    # self.tmodel.count(Address.address_id, "sumAddress"),
                    self.tmodel.count(Address.City, "sumCities"),
                    Address.City.Country.country,
                ),
                flavour=Response,
            )
            return _query, self.tmodel.query

        res, query_ = query("spain")

        self.assertEqual(res, Response(pkAddress=100, addressIdMax=200, addressIdMin=100))

    def test_complex_3(self):
        class Response(BaseModel):
            countryName: str
            contar: int

        count = Column(column_name="contar")
        res = (
            self.tmodel.order("contar", OrderType.DESC)
            .groupby(Address.City.Country.country)
            .having(count == 1)
            .first(
                (
                    self.tmodel.alias(Address.City.Country.country, "countryName"),
                    self.tmodel.count(alias_clause="contar"),
                ),
                flavour=Response,
            )
        )

        pass


if __name__ == "__main__":
    unittest.main()
