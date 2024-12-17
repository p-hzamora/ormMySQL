from datetime import datetime
import unittest
import sys
from pathlib import Path
from parameterized import parameterized

from shapely import Point

sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from models import Address, City, TableType  # noqa: E402
from ormlambda.databases.my_sql.clauses.ST_Contains import ST_Contains  # noqa: E402

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    def test_simple_condition(self):
        comparer = City.last_update >= datetime(2024, 1, 16)
        mssg: str = "city.last_update >= '2024-01-16 00:00:00'"
        self.assertEqual(comparer.query, mssg)

    def test_condition_with_and_and_or(self):
        comparer = (City.last_update >= datetime(2024, 1, 16)) & (City.city_id <= 100) | (City.Country.country == "asdf")  # noqa: F821
        mssg: str = "city.last_update >= '2024-01-16 00:00:00' AND city.city_id <= 100 OR country.country = 'asdf'"
        self.assertEqual(comparer.query, mssg)

    def test_condition_with_ST_Contains(self):
        comparer = ST_Contains(TableType.points, Point(5, -5))
        mssg: str = "ST_Contains(table_type.points, ST_GeomFromText('POINT (5 -5)'))"
        self.assertEqual(comparer.query, mssg)

    # def test_retrieve_string_from_class_property(self):
    #     comparer = (1, 2, 3, 4, 5, 6, 7) in Address.city_id
    #     mssg: str = "address.city_id in (1, 2, 3, 4, 5, 6, 7)"
    #     self.assertEqual(comparer.query, mssg)

    def test_AAretrieve_string_from_class_property_using_variable(self):
        VAR = 10
        compare = Address.city_id == VAR
        self.assertEqual(compare.query, "address.city_id = 10")

    @parameterized.expand(
        [
            ("address_id", 200),
            ("address", "Calle Cristo de la victoria"),
            ("address2", None),
            ("district", None),
            ("city_id", 1),
            ("postal_code", "28026"),
            ("phone", "617128992"),
            ("location", "Usera"),
            ("last_update", None),
        ]
    )
    def test_retrieve_value_from_instance_property(self, attr, result):
        value = getattr(ADDRESS_1, attr)
        self.assertEqual(value, result)

    def test_get_dot_chain(self):
        compare = Address.City.Country.country == "morning"
        mssg: str = "country.country = 'morning'"
        self.assertEqual(compare.query, mssg)


if __name__ == "__main__":
    unittest.main()