from datetime import datetime
import unittest
import sys
from pathlib import Path
from parameterized import parameterized

from shapely import Point


sys.path.insert(0, new_file := [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.comparer import Comparer  # noqa: E402
from test.models import Address, City, TableType, A  # noqa: E402
from ormlambda.databases.my_sql.clauses.ST_Contains import ST_Contains  # noqa: E402
from ormlambda.dialects import mysql

DIALECT = mysql.dialect

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


class TestComparer(unittest.TestCase):
    def test_comparer(self) -> None:
        cond = A.pk_a == 100
        self.assertIsInstance(cond, Comparer)  # noqa: F821

    def test_raise_ValueError(self):
        with self.assertRaises(ValueError) as err:
            Comparer.join_comparers(A.pk_a == 20)

        mssg: str = "Excepted 'Comparer' iterable not Comparer"
        self.assertEqual(err.exception.args[0], mssg)

    def test_simple_condition(self):
        comparer = City.last_update >= datetime(2024, 1, 16)
        mssg: str = "city.last_update >= '2024-01-16 00:00:00'"
        self.assertEqual(comparer.query(DIALECT), mssg)

    def test_condition_with_and_and_or(self):
        comparer = (City.last_update >= datetime(2024, 1, 16)) & (City.city_id <= 100) | (City.Country.country == "asdf")  # noqa: F821
        mssg: str = "city.last_update >= '2024-01-16 00:00:00' AND city.city_id <= 100 OR country.country = 'asdf'"
        self.assertEqual(comparer.query(DIALECT), mssg)

    def test_condition_with_ST_Contains(self):
        comparer = ST_Contains(TableType.points, Point(5, -5), dialect=DIALECT)
        mssg: str = "ST_Contains(ST_AsText(table_type.points), ST_AsText(%s))"
        self.assertEqual(comparer.query, mssg)

    # def test_retrieve_string_from_class_property(self):
    #     comparer = (1, 2, 3, 4, 5, 6, 7) in Address.city_id
    #     mssg: str = "address.city_id in (1, 2, 3, 4, 5, 6, 7)"
    #     self.assertEqual(comparer.query(DIALECT), mssg)

    def test_retrieve_string_from_class_property_using_variable(self):
        VAR = 10
        compare = Address.city_id == VAR
        self.assertEqual(compare.query(DIALECT), "address.city_id = 10")

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
        compare = Address.City.Country.country == "morning"
        mssg: str = "country.country = 'morning'"
        self.assertEqual(compare.query(DIALECT), mssg)

    def test_join_some_Comparer_object(self) -> None:
        VAR = "Madrid"
        compare1 = Address.address == "Tetuan"
        compare2 = Address.City.city == VAR
        compare3 = Address.City.Country.country == "Spain"

        comparer = type(compare1).join_comparers([compare1, compare2, compare3], True)
        self.assertEqual(comparer, "address.address = 'Tetuan' AND city.city = 'Madrid' AND country.country = 'Spain'")


if __name__ == "__main__":
    unittest.main()
