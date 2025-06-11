import unittest
import sys
from pathlib import Path


sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext  # noqa: E402
from ormlambda.sql.comparer import Regex, Like  # noqa: E402
from test.models import (  # noqa: E402
    Address,
    City,
    Country,
    B,
    C,
)
from ormlambda.sql.clauses.where import Where  # noqa: E402
from ormlambda.sql.comparer import Comparer  # noqa: E402
from ormlambda import ForeignKey  # noqa: E402
from ormlambda.dialects import mysql  # noqa: E402

DIALECT = mysql.dialect


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


class TestWhere(unittest.TestCase):
    def tearDown(self):
        ForeignKey.stored_calls.clear()

    def test_one_where(self):
        w = Where(Address.address == 10)
        self.assertEqual(w.query(DIALECT), "WHERE address.address = 10")

    def test_multiples_where(self):
        w = Where(
            Address.address == "madrid",
            Address.address2 == "other",
            Address.district == 1000,
            Address.city_id == 87,
        )
        self.assertEqual(w.query(DIALECT), "WHERE address.address = 'madrid' AND address.address2 = 'other' AND address.district = 1000 AND address.city_id = 87")

    def test_where_with_different_table_base(self):
        w = Where(
            Address.address == "sol",
            Address.City.city == "Madrid",
        )
        self.assertEqual(w.query(DIALECT), "WHERE address.address = 'sol' AND city.city = 'Madrid'")

    def test_where_with_different_tables_recursive(self):
        address = "sol"
        city = "Madrid"
        country = "Spain"
        w = Where(
            Address.address == address,
            Address.City.city == city,
            Address.City.Country.country == country,
        )
        self.assertEqual(w.query(DIALECT), "WHERE address.address = 'sol' AND city.city = 'Madrid' AND country.country = 'Spain'")

    def test_where_with_regex(self):
        pattern: str = r"^[A+]"
        w = Where(Regex(Address.address, pattern))
        self.assertEqual(w.query(DIALECT), f"WHERE address.address REGEXP '{pattern}'")

    def test_where_with_regex_from_column(self):
        pattern: str = r"^[A+]"
        w = Where(Address.address.regex(pattern))
        self.assertEqual(w.query(DIALECT), f"WHERE address.address REGEXP '{pattern}'")

    def test_where_with_like(self):
        pattern: str = r"*123*"
        w = Where(Like(Address.address, pattern))
        self.assertEqual(w.query(DIALECT), f"WHERE address.address LIKE '{pattern}'")

    def test_where_with_like_from_column(self):
        pattern: str = r"*123*"
        w = Where(Address.address.like(pattern))
        self.assertEqual(w.query(DIALECT), f"WHERE address.address LIKE '{pattern}'")

    def test_where_contains(self):
        w = Where(Address.address_id.contains((1, 2, 3, 4, 5, 6, 7, 8, 9)))
        self.assertEqual(w.query(DIALECT), "WHERE address.address_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")

    def test_where_not_contains(self):
        w = Where(Address.address_id.not_contains((1, 2, 3, 4, 5, 6, 7, 8, 9)))
        self.assertEqual(w.query(DIALECT), "WHERE address.address_id NOT IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


class TestCondition(unittest.TestCase):
    COND_CI_CO: Comparer = City.last_update != Country.country_id
    COND_A_CI: Comparer = Address.address2 <= City.city_id
    COND_B_C: Comparer = B.A.value == C.B.data

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_CI_CO, Comparer)
        self.assertIsInstance(self.COND_A_CI, Comparer)
        self.assertIsInstance(self.COND_B_C, Comparer)

    def test_to_query_cond_1(self):
        self.assertEqual(Where(self.COND_CI_CO).query(DIALECT), "WHERE city.last_update != country.country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(Where(self.COND_A_CI).query(DIALECT), "WHERE address.address2 <= city.city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(Where(self.COND_B_C).query(DIALECT), "WHERE a.value = b.data")

    def test_join_condition_restrictive_false(self):
        joins = Where(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=False)
        self.assertEqual(joins.query(DIALECT), "WHERE city.last_update != country.country_id OR address.address2 <= city.city_id OR a.value = b.data")

    def test_join_condition_restrictive_true(self):
        joins = Where(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=True)
        self.assertEqual(joins.query(DIALECT), "WHERE city.last_update != country.country_id AND address.address2 <= city.city_id AND a.value = b.data")

    def test_value_replace(self):
        cond = Where(Address.city_id == City.city_id)
        self.assertEqual(cond.query(DIALECT), "WHERE address.city_id = city.city_id")

        city = City(1, "Madrid", 50)
        cond_2 = city.city_id == city.country_id
        self.assertEqual(cond_2, False)

    def test_value_replace_2(self):
        country = Country(50, "Espanna")

        cond_2 = Where((ADDRESS_1.city_id != City.city_id) & (City.city_id <= country.country_id))
        self.assertEqual(cond_2.query(DIALECT), "WHERE city.city_id != 1 AND city.city_id <= 50")

    # def test_like_condition(self):
    #     country = Country(50, "Espanna")

    #     cond_2 = Where(Address.city_id, ConditionType.REGEXP, country.country)
    #     self.assertEqual(cond_2.query(DIALECT), "WHERE address.city_id REGEXP 'Espanna'")

    # def test_raise_KeyError(self):
    #     with self.assertRaises(KeyError):
    #         Where((Address.city_id != City.city_id) & (City.city_id<= Country.country_id) & (Country.country_id == 3)).query

    def test_replace_address(self):
        cond = Where(City.city == ADDRESS_1.address)
        self.assertEqual(cond.query(DIALECT), "WHERE city.city = 'Calle Cristo de la victoria'")

    def test_wrapped_string_variable_content(self):
        variable_ = "var_string"
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query(DIALECT), "WHERE city.city > 'var_string'")

    def test_wrapped_string_const_content(self):
        cond = Where(City.city > "var_string")
        self.assertEqual(cond.query(DIALECT), "WHERE city.city > 'var_string'")

    def test_wrapped_distinct_from_string_variable_content(self):
        variable_ = 1000
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query(DIALECT), "WHERE city.city > 1000")

    def test_wrapped_distinct_from_string_const_content(self):
        cond = Where(City.city > 1000)
        self.assertEqual(cond.query(DIALECT), "WHERE city.city > 1000")

    def test_replace_variable(self):
        variable_ = "var_string"
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query(DIALECT), "WHERE city.city > 'var_string'")

    def test_pass_multiples_comparers(self):
        ctx = ClauseInfoContext(
            table_context={
                Address: "address",
                City: "city",
                Country: "country",
            }
        )
        cond = Where(
            Address.address_id >= 40,
            Address.address_id < 100,
            Address.City.city_id >= 30,
            Address.City.city_id < 100,
            Address.City.Country.country_id >= 60,
            Address.City.Country.country_id < 100,
            context=ctx,
        )
        self.assertEqual(cond.query(DIALECT), "WHERE `address`.address_id >= 40 AND `address`.address_id < 100 AND `city`.city_id >= 30 AND `city`.city_id < 100 AND `country`.country_id >= 60 AND `country`.country_id < 100")


if __name__ == "__main__":
    unittest.main()
