import unittest
import sys
from pathlib import Path


sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.common.abstract_classes.comparer import Regex, Like  # noqa: E402
from models import Address  # noqa: E402
from ormlambda.databases.my_sql.clauses.where import Where  # noqa: E402

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestWhere(unittest.TestCase):
    def test_one_where(self):
        w = Where(Address.address == 10)
        self.assertEqual(w.query, "WHERE address.address = 10")

    def test_multiples_where(self):
        w = Where(
            Address.address == "madrid",
            Address.address2 == "other",
            Address.district == 1000,
            Address.city_id == 87,
        )
        self.assertEqual(w.query, "WHERE address.address = 'madrid' AND address.address2 = 'other' AND address.district = 1000 AND address.city_id = 87")

    def test_where_with_different_table_base(self):
        w = Where(
            Address.address == "sol",
            Address.City.city == "Madrid",
        )
        self.assertEqual(w.query, "WHERE address.address = 'sol' AND city.city = 'Madrid'")

    def test_where_with_different_tables_recursive(self):
        address = "sol"
        city = "Madrid"
        country = "Spain"
        w = Where(
            Address.address == address,
            Address.City.city == city,
            Address.City.Country.country == country,
        )
        self.assertEqual(w.query, "WHERE address.address = 'sol' AND city.city = 'Madrid' AND country.country = 'Spain'")

    def test_where_with_regex(self):
        pattern: str = r"^[A+]"
        w = Where(Regex(Address.address, pattern))
        self.assertEqual(w.query, f"WHERE address.address REGEXP '{pattern}'")

    def test_where_with_regex_from_column(self):
        pattern: str = r"^[A+]"
        w = Where(Address.address.regex(pattern))
        self.assertEqual(w.query, f"WHERE address.address REGEXP '{pattern}'")

    def test_where_with_like(self):
        pattern: str = r"*123*"
        w = Where(Like(Address.address, pattern))
        self.assertEqual(w.query, f"WHERE address.address LIKE '{pattern}'")

    def test_where_with_like_from_column(self):
        pattern: str = r"*123*"
        w = Where(Address.address.like(pattern))
        self.assertEqual(w.query, f"WHERE address.address LIKE '{pattern}'")

    def test_where_contains(self):
        w = Where(Address.address_id.contains((1, 2, 3, 4, 5, 6, 7, 8, 9)))
        self.assertEqual(w.query, "WHERE address.address_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")

    def test_where_not_contains(self):
        w = Where(Address.address_id.not_contains((1, 2, 3, 4, 5, 6, 7, 8, 9)))
        self.assertEqual(w.query, "WHERE address.address_id NOT IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")


if __name__ == "__main__":
    unittest.main()
