from __future__ import annotations
import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.engine import create_engine
from ormlambda import ORM

from test.env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)


from test.models import Address


class TestEngine(unittest.TestCase):
    def test_create_engine(self) -> None:
        url_connection = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
        db = create_engine(url_connection)

        ORM(Address, db).select(Address.City.Country.country)

        # ORM(Address, db).select(
        #     lambda x: (
        #         x.address,
        #         x.City.city,
        #         x.City.Country.country,
        #     ),
        # )


if __name__ == "__main__":
    unittest.main()
