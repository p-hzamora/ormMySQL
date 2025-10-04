from datetime import datetime
import unittest
import sys
from pathlib import Path
from parameterized import parameterized

from shapely import Point


sys.path.insert(0, new_file := [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.caster.caster import GlobalChecker
from ormlambda.sql.comparer import Comparer  # noqa: E402
from test.models import Address, City, TableType, A  # noqa: E402
from ormlambda.dialects.mysql.clauses.ST_Contains import ST_Contains  # noqa: E402
from ormlambda.dialects import mysql


DIALECT = mysql.dialect

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


class TestComparer(unittest.TestCase):
    def test_comparer(self) -> None:
        cond = GlobalChecker.resolved_callback_object(A, lambda x: x.pk_a == 100)[0]
        self.assertIsInstance(cond, Comparer)  # noqa: F821

    def test_raise_ValueError(self):
        with self.assertRaises(ValueError) as err:
            Comparer.join_comparers(A.pk_a == 20, dialect=DIALECT)

        mssg: str = "Excepted 'Comparer' iterable not Comparer"
        self.assertEqual(err.exception.args[0], mssg)

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

    def test_condition_with_ST_Contains(self):
        col = GlobalChecker[TableType].resolved_callback_object(TableType, lambda x: x.points)[0]
        comparer = ST_Contains(col, Point(5, -5))
        mssg: str = "ST_Contains(ST_AsText(`table_type`.points), ST_AsText(%s))"
        self.assertEqual(comparer.compile(DIALECT).string, mssg)

    # def test_retrieve_string_from_class_property(self):
    #     comparer = (1, 2, 3, 4, 5, 6, 7) in Address.city_id
    #     mssg: str = "`address`.city_id in (1, 2, 3, 4, 5, 6, 7)"
    #     self.assertEqual(comparer.compile(DIALECT).string, mssg)

    def test_retrieve_string_from_class_property_using_variable(self):
        VAR = 10
        compare = GlobalChecker[Address].resolved_callback_object(Address, lambda x: x.city_id == VAR)[0]
        self.assertEqual(compare.compile(DIALECT).string, "`address`.city_id = 10")

    @parameterized.expand(
        [
            ("address_id", 200),
            ("address", "Calle Cristo de la victoria"),
            ("address2", "Usera"),
            ("district", None),
            ("city_id", 1),
            ("postal_code", "28026"),
            ("phone", "617128992"),
            ("location", None),
            ("last_update", None),
        ]
    )
    def test_retrieve_value_from_instance_property(self, attr, result):
        value = getattr(ADDRESS_1, attr)
        self.assertEqual(value, result)

    def test_get_dot_chain(self):
        col = GlobalChecker[Address].resolved_callback_object(Address, lambda x: x.City.Country.country == "morning")[0]

        mssg: str = "`address_City_Country`.country = 'morning'"
        self.assertEqual(col.compile(DIALECT).string, mssg)

    def test_join_some_Comparer_object(self) -> None:
        VAR = "Madrid"

        cols = GlobalChecker[Address].resolved_callback_object(
            Address,
            lambda x: (
                x.address == "Tetuan",
                x.City.city == VAR,
                x.City.Country.country == "Spain",
            ),
        )
        comparer = Comparer.join_comparers(cols, True, dialect=DIALECT)
        self.assertEqual(comparer, "`address`.address = 'Tetuan' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain'")

    def test_join_some_Comparer_object_using_column_proxy(self) -> None:
        VAR = "Madrid"

        def foo(address: Address):
            return (
                address.address == "Tetuan",
                address.City.city == VAR,
                address.City.Country.country == "Spain",
            )

        resolved_proxy = GlobalChecker.resolved_callback_object(Address, foo)
        comparer = Comparer.join_comparers(
            resolved_proxy,
            True,
            dialect=DIALECT,
        )

        self.assertEqual(comparer, "`address`.address = 'Tetuan' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain'")


if __name__ == "__main__":
    unittest.main()
