from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM, Column
from test.models import Address  # noqa: E402

from test.config import create_sakila_engine
from pydantic import BaseModel


class TestGroupby(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        engine = create_sakila_engine()

        cls.model = ORM(Address, engine)

    def test_groupby(self) -> None:
        class Response(BaseModel):
            district: str
            count: int

        count_name = Column(column_name="count")

        res = (
            self.model.groupby(Address.district)
            .order(count_name, "DESC")
            .having(count_name >= 5)
            .select(
                (
                    Address.district,
                    self.model.count(Address.address),
                ),
                flavour=Response,
            )
        )

        TOTAL_SUM = sum(x.count for x in res)

        class Response2(BaseModel):
            district: str
            address: str

        results = [r.district for r in res]
        res2 = self.model.where(Address.district.contains(results)).order(Address.district, "DESC").select((Address.district, Address.address), flavour=Response2)
        EXPECTED = len(res2)
        self.assertEqual(TOTAL_SUM, EXPECTED)


if __name__ == "__main__":
    unittest.main(failfast=False)
