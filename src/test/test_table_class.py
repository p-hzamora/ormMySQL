import unittest
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Column  # noqa: E402
from ormlambda import Table  # noqa: E402
from ormlambda.sql.table import TableMeta  # noqa: E402


class Person(Table):
    __table_name__ = "person"

    pk_id: Optional[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str] = Column(str)
    age: Column[int] = Column(int)
    email: Column[str] = Column(str)
    phone: Column[str] = Column(str)
    address: Column[str] = Column(str)


P1 = Person(None, "Pablo", 25, "pablo@icloud.com", "6XXXXXXXXX", "C/ Madrid N_1, 3B")
P2 = Person(None, "Pablo", 25, "pablo@icloud.com", "6XXXXXXXXX", "C/ Madrid N_1, 3B")


class TestTableConstructor(unittest.TestCase):
    def test_initialize_person(self):
        self.assertIsInstance(P1, Table)

    def test_if_two_objects_are_equals(self):
        self.assertEqual(P1, P2)

    def test_if_two_objects_are_not_the_same(self):
        self.assertIsNot(P1, P2)

    def test_if_Person_is_subclass_of_Table(self):
        self.assertTrue(issubclass(Person, Table))

    def test_if_instance_of_person_is_subclass_of_Table(self):
        self.assertTrue(isinstance(P1, Table))

    def test_Person_is_type_of_TableMeta(self):
        self.assertTrue(type(Table), TableMeta)

    def test_TableMeta_type_is_type(self):
        self.assertTrue(type(TableMeta), type)


if __name__ == "__main__":
    unittest.main()
