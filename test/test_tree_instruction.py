import sys
from pathlib import Path
from datetime import datetime
import unittest
import dis 

sys.path.append(str(Path(__file__).parent.parent))

from orm.dissambler.tree_instruction import TreeInstruction  # noqa: E402
from orm.dissambler.nested_element import NestedElement  # noqa: E402


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


class TestTreeInstruction(unittest.TestCase):
    COMPLEX_BYTECODE: dis.Bytecode = dis.Bytecode(
        lambda class_x, class_b, class_c: (
            class_c.item,
            class_c.fk_class_b.item_from_class_b.a.s.d.f.g.h.j.k.l.q,
            class_b.item,
            class_x.a,
            class_x.b,
            class_x.c,
        )
    )

    def test_create_method(self):
        byte_code = dis.Bytecode(lambda a, b: (a.foo_a, b.foo_b))
        tree = TreeInstruction(byte_code, dtype=tuple).to_dict()

        self.assertEqual(tree["a"][0].name, "foo_a")
        self.assertEqual(tree["b"][0].name, "foo_b")

    def test_create_method_isinstance(self):
        tree = TreeInstruction(self.COMPLEX_BYTECODE, list).to_dict()
        self.assertIsInstance(tree, dict)

        self.assertIsInstance(tree["class_c"], list)
        self.assertIsInstance(tree["class_b"], list)
        self.assertIsInstance(tree["class_x"], list)

        self.assertIsInstance(tree["class_c"][0], NestedElement)
        self.assertIsInstance(tree["class_c"][1], NestedElement)
        self.assertIsInstance(tree["class_b"][0], NestedElement)
        self.assertIsInstance(tree["class_x"][0], NestedElement)
        self.assertIsInstance(tree["class_x"][1], NestedElement)
        self.assertIsInstance(tree["class_x"][2], NestedElement)

        self.assertIsInstance(tree["class_c"][0].name, str)
        self.assertIsInstance(tree["class_b"][0].name, str)
        self.assertIsInstance(tree["class_x"][0].name, str)

    def test_to_list(self):
        byte_code = dis.Bytecode(lambda a, b: (a.foo_a, b.foo_b))
        tree = TreeInstruction(byte_code, dtype=tuple).to_list()

        self.assertEqual(tree[0].var, "a")
        self.assertEqual(tree[1].var, "b")

        self.assertEqual(tree[0].nested_element.name, "foo_a")
        self.assertEqual(tree[1].nested_element.name, "foo_b")

    def test_const(self):
        byte_code = dis.Bytecode(lambda x: ("6", 123, x.a, x.b.c.d.e))
        tree = TreeInstruction(byte_code, dtype=tuple).to_list()

        self.assertEqual(tree[0].var, "6")
        self.assertEqual(tree[1].var, 123)

        self.assertEqual(tree[2].var, "x")
        self.assertEqual(tree[3].var, "x")
        self.assertEqual(tree[2].nested_element.name, "a")
        self.assertEqual(tree[3].nested_element.name, "e")
        self.assertEqual(tree[3].nested_element.parent.name, "d")
        self.assertEqual(tree[3].nested_element.parent.parent.name, "c")
        self.assertEqual(tree[3].nested_element.parent.parent.parent.name, "b")

    def test_const_and_var(self):
        byte_code = dis.Bytecode(lambda x: "6" == x.a.b.c)
        tree = TreeInstruction(byte_code, dtype="COMPARABLE").to_list()

        self.assertEqual(tree[0].nested_element.name, "6")
        self.assertEqual(tree[1].nested_element.name, "c")


if __name__ == "__main__":
    unittest.main()
