import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.condition_types import ConditionType  # noqa: E402
from orm.orm_objects.queries import WhereCondition  # noqa: E402
from test.models import City, Country, Address  # noqa: E402


class C:
    c: str
    data: str


class B:
    b: str
    c: C
    value: None


class A:
    a: str
    b: B


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    COND_1 = WhereCondition[City, Country](lambda x, y: x.last_update != y.country_id)
    COND_2 = WhereCondition[Address, City](lambda a, c: a.address2 <= c.city_id)
    COND_3 = WhereCondition[A, B](lambda a, b: a.b.value == b.c.data)

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_1, WhereCondition)
        self.assertIsInstance(self.COND_2, WhereCondition)
        self.assertIsInstance(self.COND_3, WhereCondition)

    def test_to_query_cond_1(self):
        self.assertEqual(self.COND_1.query, "WHERE last_update != country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(self.COND_2.query, "WHERE address2 <= city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(self.COND_3.query, "WHERE value = data")

    def test_join_condition_restrictive_false(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=False)
        self.assertEqual(joins, "WHERE (last_update != country_id) OR (address2 <= city_id) OR (value = data)")

    def test_join_condition_restrictive_true(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=True)
        self.assertEqual(joins, "WHERE (last_update != country_id) AND (address2 <= city_id) AND (value = data)")

    def test_value_replace(self):
        cond = WhereCondition[Address, City](lambda a, ci: a.city_id == ci.city_id)
        self.assertEqual(cond.query, "WHERE city_id = city_id")

        city = City(1, "Madrid", 50)
        cond_2 = WhereCondition[Address, City](lambda a, ci: a.city_id == ci.country_id, a=ADDRESS_1, ci=city)
        self.assertEqual(cond_2.query, "WHERE 1 = 50")

    def test_value_replace_2(self):
        country = Country(50, "Espanna")

        cond_2 = WhereCondition[Address, City, Country](lambda a, ci, co: a.city_id != ci.city_id <= co.country_id, a=ADDRESS_1, co=country)
        self.assertEqual(cond_2.query, "WHERE (1 != city_id) AND (city_id <= 50)")

    def test_like_condition(self):
        country = Country(50, "Espanna")

        cond_2 = WhereCondition[Address, Country](lambda a, c: (a.city_id,ConditionType.REGEXP, c.country), c=country)
        self.assertEqual(cond_2.query, "WHERE city_id REGEXP Espanna")

    def test_raise_KeyError(self):
        with self.assertRaises(KeyError):
            WhereCondition[Address, City, Country](lambda a, ci, co: a.city_id != ci.city_id <= co.country_id == 3).query

    def test_replace_address(self):
        cond=  WhereCondition[City,Address](lambda c,a: c.city == a.address, a=ADDRESS_1)
        self.assertEqual(cond.query, "WHERE city = Calle Cristo de la victoria")

if __name__ == "__main__":
    unittest.main()
