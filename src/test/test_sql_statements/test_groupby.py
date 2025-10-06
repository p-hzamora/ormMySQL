from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM, Count
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

        # fmt: off
        res = (
            self.model
            .groupby(lambda x: x.district)
            .order(lambda x: x.count, "DESC")
            .having(lambda x: x.count >= 5)
            .select(lambda x:
                (
                    x.district,
                    Count(x.address),
                ),
                flavour=Response,
            )
        )
        # fmt: on

        TOTAL_SUM = sum(x.count for x in res)

        class Response2(BaseModel):
            district: str
            address: str

        results = [r.district for r in res]
        # fmt: off
        res2 = (
            self.model
            .where(lambda x: x.district.contains(results))
            .order(lambda x:x.district, "DESC")
            .select(lambda x: 
                    (
                        x.district,
                        x.address
                    ),
                    flavour=Response2)
        )
        # fmt: on
        EXPECTED = len(res2)
        self.assertEqual(TOTAL_SUM, EXPECTED)


if __name__ == "__main__":
    unittest.main(failfast=False)
