import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

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


address = Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid")
address = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)
city = City(1, "Madrid", 50)
country = Country(50, "Espanna")



class TestCondition(unittest.TestCase):
    COND_1 = WhereCondition[City, Country](City, Country, lambda_function=lambda x, y: x.last_update != y.country_id)
    COND_2 = WhereCondition[Address, City](Address, City, lambda_function=lambda a, c: a.address2 <= c.city_id)
    COND_3 = WhereCondition[A, B](A, B, lambda_function=lambda a, b: a.b.value == b.c.data)

    def test_condition_constructor(self):
        self.assertIsInstance(self.COND_1, WhereCondition)
        self.assertIsInstance(self.COND_2, WhereCondition)
        self.assertIsInstance(self.COND_3, WhereCondition)

    def test_to_query_cond_1(self):
        self.assertEqual(self.COND_1.to_query(), "WHERE last_update != country_id")

    def test_to_query_cond_2(self):
        self.assertEqual(self.COND_2.to_query(), "WHERE address2 <= city_id")

    def test_to_query_cond_3(self):
        self.assertEqual(self.COND_3.to_query(), "WHERE value = data")

    def test_join_condition_restrictive_false(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=False)
        self.assertEqual(joins, "WHERE (last_update != country_id) OR (address2 <= city_id) OR (value = data)")

    def test_join_condition_restrictive_true(self):
        joins = WhereCondition.join_condition(self.COND_1, self.COND_2, self.COND_3, restrictive=True)
        self.assertEqual(joins, "WHERE (last_update != country_id) AND (address2 <= city_id) AND (value = data)")


if __name__ == "__main__":
    unittest.main()
