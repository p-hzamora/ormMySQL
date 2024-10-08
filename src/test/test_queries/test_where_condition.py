import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.common.enums import ConditionType  # noqa: E402
from ormlambda.databases.my_sql.clauses import WhereCondition  # noqa: E402
from models import City, Country, Address, B, C  # noqa: E402

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    COND_CI_CO = WhereCondition[City, Country](instances=(City, Country), function=lambda x, y: x.last_update != y.country_id)
    COND_A_CI = WhereCondition[Address, City](instances=(Address, City), function=lambda a, c: a.address2 <= c.city_id)
    COND_B_C = WhereCondition[B, C](instances=(B, C), function=lambda b, c: b.A.value == c.B.data)

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_CI_CO, WhereCondition)
        self.assertIsInstance(self.COND_A_CI, WhereCondition)
        self.assertIsInstance(self.COND_B_C, WhereCondition)

    def test_to_query_cond_1(self):
        self.assertEqual(self.COND_CI_CO.query, "WHERE city.last_update != country.country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(self.COND_A_CI.query, "WHERE address.address2 <= city.city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(self.COND_B_C.query, "WHERE a.value = b.data")

    def test_join_condition_restrictive_false(self):
        joins = WhereCondition.join_condition(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=False)
        self.assertEqual(joins, "WHERE (city.last_update != country.country_id) OR (address.address2 <= city.city_id) OR (a.value = b.data)")

    def test_join_condition_restrictive_true(self):
        joins = WhereCondition.join_condition(self.COND_CI_CO, self.COND_A_CI, self.COND_B_C, restrictive=True)
        self.assertEqual(joins, "WHERE (city.last_update != country.country_id) AND (address.address2 <= city.city_id) AND (a.value = b.data)")

    def test_value_replace(self):
        cond = WhereCondition[Address, City](instances=(Address, City), function=lambda a, ci: a.city_id == ci.city_id)
        self.assertEqual(cond.query, "WHERE address.city_id = city.city_id")

        city = City(1, "Madrid", 50)
        cond_2 = WhereCondition[Address, City](instances=(Address, City), function=lambda a, ci: a.city_id == ci.country_id, a=ADDRESS_1, ci=city)
        self.assertEqual(cond_2.query, "WHERE 1 = 50")

    def test_value_replace_2(self):
        country = Country(50, "Espanna")

        cond_2 = WhereCondition[Address, City, Country](
            instances=(Address, City, Country),
            function=lambda a, ci, co: a.city_id != ci.city_id <= co.country_id,
            a=ADDRESS_1,
            co=country,
        )
        self.assertEqual(cond_2.query, "WHERE (1 != city.city_id) AND (city.city_id <= 50)")

    def test_like_condition(self):
        country = Country(50, "Espanna")

        cond_2 = WhereCondition[Address, Country](instances=(Address, Country), function=lambda a, c: (a.city_id, ConditionType.REGEXP, c.country), c=country)
        self.assertEqual(cond_2.query, "WHERE address.city_id REGEXP 'Espanna'")

    def test_raise_KeyError(self):
        with self.assertRaises(KeyError):
            WhereCondition[Address, City, Country](instances=(Address, City, Country), function=lambda a, ci, co: a.city_id != ci.city_id <= co.country_id == 3).query

    def test_replace_address(self):
        cond = WhereCondition[City, Address](instances=(City, Address), function=lambda c, a: c.city == a.address, a=ADDRESS_1)
        self.assertEqual(cond.query, "WHERE city.city = 'Calle Cristo de la victoria'")

    def test_wrapped_string_variable_content(self):
        variable_ = "var_string"
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > variable_, variable_=variable_)
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")

    def test_wrapped_string_const_content(self):
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > "var_string")
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")

    def test_wrapped_distinct_from_string_variable_content(self):
        variable_ = 1000
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > variable_, variable_=variable_)
        self.assertEqual(cond.query, "WHERE city.city > 1000")

    def test_wrapped_distinct_from_string_const_content(self):
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > 1000)
        self.assertEqual(cond.query, "WHERE city.city > 1000")

    def test_no_replace_variable(self):
        variable_ = "var_string"
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > variable_)
        self.assertEqual(cond.query, "WHERE city.city > 'variable_'")


if __name__ == "__main__":
    unittest.main()
