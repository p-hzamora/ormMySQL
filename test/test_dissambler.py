import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from orm.orm_objects.queries.dissambler import Dissambler
from datetime import datetime


class A:
    a_id: str
    a_data: str
    a_time: datetime


class B:
    b_id: int
    b_data: str
    b_time: datetime


class CtoB:
    c_id: int
    c_data: str
    c_time: datetime
    b: B = B


class DtoC:
    d_id: int
    d_data: str
    d_time: datetime
    c: CtoB = CtoB


class TestDissambler(unittest.TestCase):
    # region Heritage_var_control
    def test_heritage_var_control_with_one_attr_to_the_right(self):
        dis = Dissambler[DtoC, None](lambda d: "asdf" != d.c.b.b_data)
        self.assertEqual(dis.cond_1, "asdf")
        self.assertEqual(dis.cond_2, "b_data")
        self.assertEqual(dis.compare_op, "!=")

    def test_heritage_var_control_with_one_attr_to_the_left(self):
        dis = Dissambler[DtoC, None](lambda d: d.c.b.b_data == "asdf")
        self.assertEqual(dis.cond_1, "b_data")
        self.assertEqual(dis.cond_2, "asdf")
        self.assertEqual(dis.compare_op, "=")

    def test_heritage_var_control_with_two_attr(self):
        dis = Dissambler[DtoC, CtoB](lambda d, c: d.c.b.b_data == c.b.b_data)
        self.assertEqual(dis.cond_1, "b_data")
        self.assertEqual(dis.cond_2, "b_data")
        self.assertEqual(dis.compare_op, "=")

    # endregion
    # region zero attributes
    def test_zero_attr(self):
        dis = Dissambler(lambda: 5 > 1)
        self.assertEqual(dis.cond_1, 5)
        self.assertEqual(dis.cond_2, 1)
        self.assertEqual(dis.compare_op, ">")

    # endregion

    # region one attribute
    def test_one_attr_to_left(self):
        dis = Dissambler[A, None](lambda x: "foo_x" != x.a_id)
        self.assertEqual(dis.cond_1, "foo_x")
        self.assertEqual(dis.cond_2, "a_id")
        self.assertEqual(dis.compare_op, "!=")

    def test_one_attr_to_right(self):
        dis = Dissambler[A, None](lambda a: "var_to_the_left" <= a.a_time)
        self.assertEqual(dis.cond_1, "var_to_the_left")
        self.assertEqual(dis.cond_2, "a_time")
        self.assertEqual(dis.compare_op, "<=")

    # endregion

    # region two attributes
    def test_two_attr_variable(self):
        dis = Dissambler[A, B](lambda a, b: a.a_data < b.b_time)
        self.assertEqual(dis.cond_1, "a_data")
        self.assertEqual(dis.cond_2, "b_time")
        self.assertEqual(dis.compare_op, "<")

    def test_two_attr_b_to_left_a_to_right(self):
        dis = Dissambler[A, B](lambda a, b: b.b_data == a.a_data)
        self.assertEqual(dis.cond_1, "b_data")
        self.assertEqual(dis.cond_2, "a_data")
        self.assertEqual(dis.compare_op, "=")

    # endregion

    # def test_get_parent_class(self):
    #     dis = Dissambler[DtoC, CtoB](lambda d, c: d.c.b.b_time == c.c_time)
    #     self.assertEqual(dis.parent, "b")
    #     self.assertEqual(dis.parent.parent, "c")
    #     self.assertEqual(dis.cond_2, "c_time")


if __name__ == "__main__":
    unittest.main()
