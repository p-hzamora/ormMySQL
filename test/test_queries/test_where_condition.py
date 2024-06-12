import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm import Table, ForeignKey  # noqa: E402
from orm.condition_types import ConditionType  # noqa: E402
from orm.orm_objects.queries import WhereCondition  # noqa: E402
from test.models import City, Country, Address  # noqa: E402


class C(Table):
    __table_name__ = "c"
    c: str
    data: str


class B(Table):
    __table_name__ = "b"
    b: str
    fk_c: int
    c = ForeignKey["B", C](__table_name__, C, lambda b, c: b.fk_c == c.c)
    value: None


class A(Table):
    __table_name__ = "a"
    a: str
    fk_b: int

    b = ForeignKey["A", B](__table_name__, B, lambda a, b: a.fk_b == b.b)


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    COND_CI_CO = WhereCondition[City, Country](instances=(City, Country), function=lambda x, y: x.last_update != y.country_id)
    COND_A_CI = WhereCondition[Address, City](instances=(Address, City), function=lambda a, c: a.address2 <= c.city_id)
    COND_A_B = WhereCondition[A, B](instances=(A, B), function=lambda a, b: a.b.value == b.c.data)

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_CI_CO, WhereCondition)
        self.assertIsInstance(self.COND_A_CI, WhereCondition)
        self.assertIsInstance(self.COND_A_B, WhereCondition)

    def test_to_query_cond_1(self):
        self.assertEqual(self.COND_CI_CO.query, "WHERE city.last_update != country.country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(self.COND_A_CI.query, "WHERE address.address2 <= city.city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(self.COND_A_B.query, "WHERE b.value = c.data")

    def test_join_condition_restrictive_false(self):
        joins = WhereCondition.join_condition(self.COND_CI_CO, self.COND_A_CI, self.COND_A_B, restrictive=False)
        self.assertEqual(joins, "WHERE (city.last_update != country.country_id) OR (address.address2 <= city.city_id) OR (b.value = c.data)")

    def test_join_condition_restrictive_true(self):
        joins = WhereCondition.join_condition(self.COND_CI_CO, self.COND_A_CI, self.COND_A_B, restrictive=True)
        self.assertEqual(joins, "WHERE (city.last_update != country.country_id) AND (address.address2 <= city.city_id) AND (b.value = c.data)")

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

    def test_replace_variable(self):
        variable_ = "var_string"
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > variable_, variable_=variable_)
        self.assertEqual(cond.query, "WHERE city.city > 'var_string'")

    def test_no_replace_variable(self):
        variable_ = "var_string"
        cond = WhereCondition[City, Address](instances=(City,), function=lambda c: c.city > variable_)
        self.assertEqual(cond.query, "WHERE city.city > variable_")


if __name__ == "__main__":
    unittest.main()
