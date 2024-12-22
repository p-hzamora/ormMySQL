import unittest
import sys
from pathlib import Path


sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.common.abstract_classes.comparer import Comparer  # noqa: E402
from ormlambda.databases.my_sql.clauses import Where  # noqa: E402
from models import City, Country, Address, B, C  # noqa: E402

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    COND_CI_CO: Comparer = City.last_update != Country.country_id
    COND_A_CI: Comparer = Address.address2 <= City.city_id
    COND_B_C: Comparer = B.A.value == C.B.data

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_CI_CO, Comparer)
        self.assertIsInstance(self.COND_A_CI, Comparer)
        self.assertIsInstance(self.COND_B_C, Comparer)

    def test_to_query_cond_1(self):
        self.assertEqual(Where(self.COND_CI_CO).query, "WHERE city.last_update != country.country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(Where(self.COND_A_CI).query, "WHERE address.address2 <= city.city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(Where(self.COND_B_C).query, "WHERE a.value = b.data")

    def test_join_condition_restrictive_false(self):
        joins = Where(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=False)
        self.assertEqual(joins.query, "WHERE city.last_update != country.country_id OR address.address2 <= city.city_id OR a.value = b.data")

    def test_join_condition_restrictive_true(self):
        joins = Where(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=True)
        self.assertEqual(joins.query, "WHERE city.last_update != country.country_id AND address.address2 <= city.city_id AND a.value = b.data")

    def test_value_replace(self):
        cond = Where(Address.city_id == City.city_id)
        self.assertEqual(cond.query, "WHERE address.city_id = city.city_id")

        city = City(1, "Madrid", 50)
        cond_2 = city.city_id == city.country_id
        self.assertEqual(cond_2, False)

    def test_value_replace_2(self):
        country = Country(50, "Espanna")

        cond_2 = Where((ADDRESS_1.city_id != City.city_id) & (City.city_id <= country.country_id))
        self.assertEqual(cond_2.query, "WHERE city.city_id != 1 AND city.city_id <= 50")

    # def test_like_condition(self):
    #     country = Country(50, "Espanna")

    #     cond_2 = Where(Address.city_id, ConditionType.REGEXP, country.country)
    #     self.assertEqual(cond_2.query, "WHERE address.city_id REGEXP 'Espanna'")

    # def test_raise_KeyError(self):
    #     with self.assertRaises(KeyError):
    #         Where((Address.city_id != City.city_id) & (City.city_id<= Country.country_id) & (Country.country_id == 3)).query

    def test_replace_address(self):
        cond = Where(City.city == ADDRESS_1.address)
        self.assertEqual(cond.query, "WHERE city.city = 'Calle Cristo de la victoria'")

    def test_wrapped_string_variable_content(self):
        variable_ = "var_string"
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")

    def test_wrapped_string_const_content(self):
        cond = Where(City.city > "var_string")
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")

    def test_wrapped_distinct_from_string_variable_content(self):
        variable_ = 1000
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query, "WHERE city.city > 1000")

    def test_wrapped_distinct_from_string_const_content(self):
        cond = Where(City.city > 1000)
        self.assertEqual(cond.query, "WHERE city.city > 1000")

    def test_replace_variable(self):
        variable_ = "var_string"
        cond = Where(City.city > variable_)
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")


if __name__ == "__main__":
    unittest.main()
