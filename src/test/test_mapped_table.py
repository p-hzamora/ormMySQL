import unittest
import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
from ormlambda import Table, Column  # noqa: E402


class Person(Table):
    __table_name__ = "person"

    id: Column[int] = Column(int, is_primary_key=True)
    title: Column[str] = Column(str)
    content: Column[str] = Column(str)
    dni_list: Column[list] = Column(list)


class TestSQLMapping(unittest.TestCase):
    PERSON_INSTANCE = Person(1, "titleCustom", "contentCustom", [1, 2, 3, 4, 5, 6])

    def test_create_orm(self):
        self.assertEqual(self.PERSON_INSTANCE.id, 1)
        self.assertEqual(self.PERSON_INSTANCE.title, "titleCustom")
        self.assertEqual(self.PERSON_INSTANCE.content, "contentCustom")
        self.assertEqual(self.PERSON_INSTANCE.dni_list, [1, 2, 3, 4, 5, 6])

    def test_column_name(self):
        self.assertEqual(Person.id.column_name, "id")
        self.assertEqual(Person.title.column_name, "title")
        self.assertEqual(Person.content.column_name, "content")
        self.assertEqual(Person.dni_list.column_name, "dni_list")

    def test_column_value(self):
        self.assertEqual(self.PERSON_INSTANCE.id, 1)
        self.assertEqual(self.PERSON_INSTANCE.title, "titleCustom")
        self.assertEqual(self.PERSON_INSTANCE.content, "contentCustom")
        self.assertEqual(self.PERSON_INSTANCE.dni_list, [1, 2, 3, 4, 5, 6])

    def test_raise_ValueError(self):
        with self.assertRaises(ValueError) as error:
            Person(id="should be pass 'int'")
        mssg: str = "The 'id' Column from 'person' table expected '<class 'int'>' type. You passed 'str' type"
        self.assertEqual(error.exception.__str__(),mssg)


if "__main__" == __name__:
    unittest.main()
