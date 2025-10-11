from datetime import datetime
import unittest
import sys
from pathlib import Path


sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.models import (  # noqa: E402
    Address,
    City,
    Country,
)
from ormlambda.sql.comparer import Comparer  # noqa: E402
from ormlambda.common import GlobalChecker  # noqa: E402
from ormlambda.dialects import mysql  # noqa: E402

from ormlambda import ORM  # noqa: E402
from test.config import create_sakila_engine  # noqa: E402

engine = create_sakila_engine()

DIALECT = mysql.dialect


from test.models import A  # noqa: E402


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


def extract_where_query_string(model: ORM) -> str:
    query: str = model.query
    return query[query.index("WHERE") :].strip()


class TestWhere(unittest.TestCase):
    def test_one_where(self):
        string = ORM(Address, engine).where(lambda x: x.address == 10).query("where")
        self.assertEqual(string, "WHERE `address`.address = 10")

    def test_multiples_where(self):
        # fmt: off
        string = (
            ORM(Address, engine)
            .where(lambda x: 
                (
                    x.address == "madrid",
                    x.address2 == "other",
                    x.district == 1000,
                    x.city_id == 87,
                ),
            )
            .where(lambda x: x.last_update >= datetime(2025,12,16),restrictive=False)
            .where(lambda x: ((x.City.city_id==1) | (x.City.Country.country != 'Spain') & (x.City.city_id == 124)),restrictive=True)
            .query("where")
        )
        # fmt: on

        self.assertEqual(
            string, "WHERE (`address`.address = 'madrid' AND `address`.address2 = 'other' AND `address`.district = 1000 AND `address`.city_id = 87) OR `address`.last_update >= '2025-12-16 00:00:00' AND (`address_City`.city_id = 1 OR `address_City_Country`.country != 'Spain' AND `address_City`.city_id = 124)"
        )

    def test_where_with_different_table_base(self):
        string = (
            ORM(Address, engine)
            .where(
                lambda x: (
                    x.address == "sol",
                    x.City.city == "Madrid",
                ),
            )
            .query("where")
        )

        self.assertEqual(string, "WHERE (`address`.address = 'sol' AND `address_City`.city = 'Madrid')")

    def test_passing_multiples_wheres_combining_AND_OR(self) -> None:
        # fmt: off
        string = (
            ORM(Address, engine)
            .where(lambda x: (x.City.Country.country.regex("^[Ss]")) & (x.City.city.like("%(%")) & (x.city_id != 388))
            .where(lambda x: x.City.city == "Madrid",False)
            .query('where')
        )

        EXPECTED = "WHERE (`address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388) OR `address_City`.city = 'Madrid'"
        self.assertEqual(string, EXPECTED)
        # fmt: on

    def test_passing_multiples_wheres_combining_AND_OR_using_other_approach(self) -> None:
        # fmt: off
        string = (
            ORM(Address, engine)
            .where(lambda x: (
                    x.City.Country.country.regex("^[Ss]"),
                    x.City.city.like("%(%"),
                    x.city_id != 388
                )
            )
            .where(lambda x: x.City.city == "Madrid",False)
            .query('where')
        )

        EXPECTED = "WHERE (`address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388) OR `address_City`.city = 'Madrid'"
        self.assertEqual(string, EXPECTED)
        # fmt: on

    def test_passing_multiples_wheres_clauses(self) -> None:
        # fmt: off
        string = (
            ORM(Address, engine)
            .where(lambda x: x.City.Country.country.regex("^[Ss]"))
            .where(lambda x: x.City.city.like("%(%"))
            .where(lambda x: x.city_id != 388)
            .where(lambda x: x.City.city == "Madrid", False)
            .query('where')
        )

        EXPECTED = "WHERE `address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388 OR `address_City`.city = 'Madrid'"
        self.assertEqual(string, EXPECTED)
        # fmt: on

    def test_where_with_different_tables_recursive(self):
        address = "sol"
        city = "Madrid"
        country = "Spain"
        string = (
            ORM(Address, engine)
            .where(
                lambda x: (
                    x.address == address,
                    x.City.city == city,
                    x.City.Country.country == country,
                )
            )
            .query("where")
        )
        self.assertEqual(string, "WHERE (`address`.address = 'sol' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain')")

    def test_where_with_regex(self):
        pattern: str = r"^[A+]"
        string = ORM(Address, engine).where(lambda x: x.address.regex(pattern)).query("where")
        self.assertEqual(string, f"WHERE `address`.address REGEXP '{pattern}'")

    def test_where_with_like(self):
        pattern: str = r"*123*"
        string = ORM(Address, engine).where(lambda x: x.address.like(pattern)).query("where")
        self.assertEqual(string, f"WHERE `address`.address LIKE '{pattern}'")

    def test_where_contains(self):
        string = ORM(Address, engine).where(lambda x: x.address_id.contains((1, 2, 3, 4, 5, 6, 7, 8, 9))).query("where")
        self.assertEqual(string, "WHERE `address`.address_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")

    def test_where_not_contains(self):
        string = ORM(Address, engine).where(lambda x: x.address_id.not_contains((1, 2, 3, 4, 5, 6, 7, 8, 9))).query("where")
        self.assertEqual(string, "WHERE `address`.address_id NOT IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


class TestCondition(unittest.TestCase):
    def test_value_replace_2(self):
        country = Country(50, "Espanna")

        string = ORM(Address, engine).where(lambda x: (ADDRESS_1.city_id != x.City.city_id) & (x.City.city_id <= country.country_id)).query("where")
        self.assertEqual(string, "WHERE (`address_City`.city_id != 1 AND `address_City`.city_id <= 50)")

    def test_like_condition(self):
        country = Country(50, "Espanna")

        string = ORM(Address, engine).where(lambda x: x.city_id.regex(country.country)).query("where")
        self.assertEqual(string, "WHERE `address`.city_id REGEXP 'Espanna'")


class TestComparer(unittest.TestCase):
    def test_comparer(self) -> None:
        cond = GlobalChecker.resolved_callback_object(A, lambda x: x.pk_a == 100)[0]
        self.assertIsInstance(cond, Comparer)  # noqa: F821

    def test_simple_condition(self):
        comparer = GlobalChecker[City].resolved_callback_object(City, lambda x: x.last_update >= datetime(2024, 1, 16))[0]
        mssg: str = "`city`.last_update >= '2024-01-16 00:00:00'"
        self.assertEqual(comparer.compile(DIALECT).string, mssg)

    def test_condition_with_and_and_or(self):
        # fmt: off
        comparer = GlobalChecker[City].resolved_callback_object(City, lambda x: (
            x.last_update >= datetime(2024, 1, 16)) & 
            (x.city_id <= 100) | 
            (x.Country.country == "asdf"))[0]  # noqa: F821
        # fmt: on
        EXPECTED: str = "`city`.last_update >= '2024-01-16 00:00:00' AND `city`.city_id <= 100 OR `city_Country`.country = 'asdf'"
        query = comparer.compile(DIALECT).string
        self.assertEqual(query, EXPECTED)

    # def test_condition_with_ST_Contains(self):
    #     string = ORM(TableType, engine).where(lambda x: x.points.contains(Point(5, -5))).query("where")
    #     mssg: str = "ST_Contains(ST_AsText(`table_type`.points), ST_AsText(%s))"
    #     self.assertEqual(string, mssg)

    def test_retrieve_string_from_class_property_using_variable(self):
        VAR = 10
        compare = GlobalChecker[Address].resolved_callback_object(Address, lambda x: x.city_id == VAR)[0]
        self.assertEqual(compare.compile(DIALECT).string, "`address`.city_id = 10")

    def test_join_some_Comparer_object_using_column_proxy(self) -> None:
        VAR = "Madrid"

        string = (
            ORM(Address, engine)
            .where(
                lambda x: (
                    x.address == "Tetuan",
                    x.City.city == VAR,
                    x.City.Country.country == "Spain",
                )
            )
            .query("where")
        )

        self.assertEqual(string, "WHERE (`address`.address = 'Tetuan' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain')")


if __name__ == "__main__":
    unittest.main()
