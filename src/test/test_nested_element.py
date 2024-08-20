import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.orm_mysql.utils.lambda_disassembler.disassembler import NestedElement  # noqa: E402


class TestCondition(unittest.TestCase):
    def test_heritage(self):
        con = NestedElement[str]("a.b.c.d")

        self.assertEqual(con.name, "d")
        self.assertEqual(con.parent.name, "c")
        self.assertEqual(con.parent.parent.name, "b")
        self.assertEqual(con.parent.parent.parent.name, "a")

    def test_pass_list_attribute(self):
        _list = ["a", "b", "c", "d"]

        con = NestedElement[list](_list)

        self.assertEqual(con.name, "d")
        self.assertEqual(con.parent.name, "c")
        self.assertEqual(con.parent.parent.name, "b")
        self.assertEqual(con.parent.parent.parent.name, "a")

    def test_heritage_with_words(self):
        con = NestedElement[str]("class_a.class_b.item_list")

        self.assertEqual(con.name, "item_list")
        self.assertEqual(con.parent.name, "class_b")
        self.assertEqual(con.parent.parent.name, "class_a")

    def test_int_as_parameter(self):
        con = NestedElement[int](5)
        self.assertEqual(con.name, 5)

    def test_raise_ValueError(self):
        with self.assertRaises(ValueError):
            NestedElement[int](5).parent

    def test_none_value(self):
        con = NestedElement[int](None)
        self.assertEqual(con.name, None)


if __name__ == "__main__":
    unittest.main()
