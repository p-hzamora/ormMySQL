from __future__ import annotations
import sys
from pathlib import Path
import unittest


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.engine import create_engine
from ormlambda import ORM
from ormlambda.dialects import mysql


from test.models import Address


class TestEngine(unittest.TestCase):
    def test_create_engine(self) -> None:
        url_connection = "mysql://root:1500@localhost:3306/sakila?pool_size=3"
        db = create_engine(url_connection)

        Address.create_table(mysql.dialect())

        # ORM(Address, db).select(
        #     lambda x: (
        #         x.address,
        #         x.City.city,
        #         x.City.Country.country,
        #     ),
        # )


if __name__ == "__main__":
    unittest.main()
