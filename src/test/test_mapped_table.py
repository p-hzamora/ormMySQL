from typing import Annotated
import unittest
import sys
from pathlib import Path
from parameterized import parameterized

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())
from ormlambda import Table, Column, INT, VARCHAR, JSON  # noqa: E402
from ormlambda import PrimaryKey


class Person(Table):
    __table_name__ = "person"

    id: Annotated[Column[INT], PrimaryKey()]
    title: Column[VARCHAR]
    content: Column[VARCHAR]
    dni_list: Column[JSON]


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

    @parameterized.expand(
        [
            ({"id": "should be <int>"}, "The 'id' Column from 'person' table, expected 'INTEGER' type. You passed 'str' type"),
            ({"title": 1}, "The 'title' Column from 'person' table, expected 'VARCHAR' type. You passed 'int' type"),
            ({"content": 1}, "The 'content' Column from 'person' table, expected 'VARCHAR' type. You passed 'int' type"),
            ({"dni_list": "should be <dict>"}, "The 'dni_list' Column from 'person' table, expected 'JSON' type. You passed 'str' type"),
        ]
    )
    def test_raise_ValueError(self, attrs, mssg):
        with self.assertRaises(ValueError) as error:
            Person(**attrs)
        self.assertEqual(str(error.exception), mssg)


if "__main__" == __name__:
    unittest.main()
