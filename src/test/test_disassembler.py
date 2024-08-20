import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.ormlambda.utils.lambda_disassembler import Disassembler  # noqa: E402


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
        dis = Disassembler[DtoC, None](lambda d: "asdf" != d.c.b.b_data)
        self.assertEqual(dis.cond_1.name, "asdf")
        self.assertEqual(dis.cond_2.name, "b_data")
        self.assertEqual(dis.compare_op, "!=")

    def test_heritage_var_control_with_one_attr_to_the_left(self):
        dis = Disassembler[DtoC, None](lambda d: d.c.b.b_data == "asdf")
        self.assertEqual(dis.cond_1.name, "b_data")
        self.assertEqual(dis.cond_2.name, "asdf")
        self.assertEqual(dis.compare_op, "=")

    def test_heritage_var_control_with_two_attr(self):
        dis = Disassembler[DtoC, CtoB](lambda d, c: d.c.b.b_data == c.b.b_data)

        self.assertEqual(dis.cond_1.name, "b_data")
        self.assertEqual(dis.cond_1.name, "b_data")
        self.assertEqual(dis.cond_1.name, "b_data")

        self.assertEqual(dis.cond_1.name, "b_data")
        self.assertEqual(dis.cond_2.name, "b_data")
        self.assertEqual(dis.compare_op, "=")

    # endregion
    # region zero attributes
    def test_zero_attr(self):
        dis = Disassembler(lambda: 5 > 1)
        self.assertEqual(dis.cond_1.name, 5)
        self.assertEqual(dis.cond_2.name, 1)
        self.assertEqual(dis.compare_op, ">")

    # endregion

    # region one attribute
    def test_one_attr_to_left(self):
        dis = Disassembler[A, None](lambda x: "foo_x" != x.a_id)
        self.assertEqual(dis.cond_1.name, "foo_x")
        self.assertEqual(dis.cond_2.name, "a_id")
        self.assertEqual(dis.compare_op, "!=")

    def test_one_attr_to_right(self):
        dis = Disassembler[A, None](lambda a: "var_to_the_left" <= a.a_time)
        self.assertEqual(dis.cond_1.name, "var_to_the_left")
        self.assertEqual(dis.cond_2.name, "a_time")
        self.assertEqual(dis.compare_op, "<=")

    # endregion

    # region two attributes
    def test_two_attr_variable(self):
        dis = Disassembler[A, B](lambda a, b: a.a_data < b.b_time)
        self.assertEqual(dis.cond_1.name, "a_data")
        self.assertEqual(dis.cond_2.name, "b_time")
        self.assertEqual(dis.compare_op, "<")

    def test_two_attr_b_to_left_a_to_right(self):
        dis = Disassembler[A, B](lambda a, b: b.b_data == a.a_data)
        self.assertEqual(dis.cond_1.name, "b_data")
        self.assertEqual(dis.cond_2.name, "a_data")
        self.assertEqual(dis.compare_op, "=")

    # endregion

    def test_get_parent_class(self):
        dis = Disassembler[DtoC, CtoB](lambda d, c: d.c.b.b_time == c.c_time)
        self.assertEqual(dis.cond_2.parent.name, "c")
        self.assertEqual(dis.cond_2.name, "c_time")

        self.assertEqual(dis.cond_1.parent.parent.parent.name, "d")
        self.assertEqual(dis.cond_1.parent.parent.name, "c")
        self.assertEqual(dis.cond_1.parent.name, "b")
        self.assertEqual(dis.cond_1.name, "b_time")

    def test_none_values(self):
        dis = Disassembler[DtoC, CtoB](lambda d, c: d.c.b.b_time is None)
        self.assertEqual(dis.cond_2.name, None)
        self.assertEqual(dis.compare_op, "IS")
        self.assertEqual(dis.cond_1.parent.parent.parent.name, "d")
        self.assertEqual(dis.cond_1.parent.parent.name, "c")
        self.assertEqual(dis.cond_1.parent.name, "b")
        self.assertEqual(dis.cond_1.name, "b_time")


if __name__ == "__main__":
    unittest.main()
