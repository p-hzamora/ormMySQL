from __future__ import annotations
from typing import Type
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.models import Address, City, Country  # noqa: F401
from ormlambda import ORM, Column, create_engine, Table

sqlite_engine = create_engine("sqlite:///src/test/test_sqlite/test.db")
mysql_engine = create_engine("mysql://root:1500@localhost:3306/sakila?pool_size=3")


def create_and_load_table(table: Type[Table]) -> None:
    global sqlite_engine
    global mysql_engine
    sqlite = ORM(table, sqlite_engine)

    if sqlite.table_exists():
        return None

    sqlite.create_table("fail")
    data = ORM(table, mysql_engine).select()

    sqlite.insert(data)


class TestSQLite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        create_and_load_table(Address)
        create_and_load_table(City)
        create_and_load_table(Country)

        cls.amodel = ORM(Address, sqlite_engine)
        return None

    def test_sqlite_query(self) -> None:
        res = self.amodel.select(
            lambda x: (
                x,
                x.City,
            )
        )

        res = (
            self.amodel.where(lambda x: x.city_id >= 312)
            .having(Column(column_name="count") > 1)
            .groupby(Address.city_id)
            .select(
                (
                    self.amodel.alias(Address.city_id, "pkCity"),
                    self.amodel.count(alias="count"),
                ),
                flavour=dict,
            )
        )

        res2 = (
            self.amodel.order(Address.address_id, "DESC")
            .where(
                [
                    Address.address_id >= 10,
                    Address.address_id <= 30,
                ]
            )
            .select(
                (
                    Address,
                    Address.City,
                ),
                flavour=dict,
                alias=lambda x: "{table}~{column}" + f"[{x.dtype.__name__}]",
            )
        )


if __name__ == "__main__":
    unittest.main()
