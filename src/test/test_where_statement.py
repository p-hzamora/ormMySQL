from __future__ import annotations
import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda.common.interfaces import IRepositoryBase
from models import Address, AddressModel  # noqa: F401

import re


class RegexFilter:
    def __init__(self, pattern: str, value: str, *kwargs) -> None:
        self._compile: re.Pattern = re.compile(pattern, *kwargs)
        self._value: str = value


class TestWhereStatement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)
        cls.tmodel = AddressModel(cls.ddbb)

    def test_where(self):
        co = "Spain"
        select = (
            self.tmodel
            .offset(3)
            .where(lambda x: x.City.Country.country == co, co=co)
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


if __name__ == "__main__":
    unittest.main()
