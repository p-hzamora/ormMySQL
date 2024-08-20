import unittest
import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]
from src.orm_mysql.utils import Table, Column  # noqa: E402


class Person(Table):
    __table_name__ = "person"

    id: int = Column[int](is_primary_key=True)
    title: int = Column[int]()
    content: int = Column[int]()
    dni_list: list = Column[list]()


class TestSQLMapping(unittest.TestCase):
    PERSON_INSTANCE: Person = Person(1, "titleCustom", "contentCustom", [1, 2, 3, 4, 5, 6])

    def test_create_orm(self):
        self.assertEqual(self.PERSON_INSTANCE.id, 1)
        self.assertEqual(self.PERSON_INSTANCE.title, "titleCustom")
        self.assertEqual(self.PERSON_INSTANCE.content, "contentCustom")
        self.assertEqual(self.PERSON_INSTANCE.dni_list, [1, 2, 3, 4, 5, 6])

    def test_column_name(self):
        self.assertEqual(self.PERSON_INSTANCE._id.column_name, "id")
        self.assertEqual(self.PERSON_INSTANCE._title.column_name, "title")
        self.assertEqual(self.PERSON_INSTANCE._content.column_name, "content")
        self.assertEqual(self.PERSON_INSTANCE._dni_list.column_name, "dni_list")

    def test_column_value(self):
        self.assertEqual(self.PERSON_INSTANCE._id.column_value, 1)
        self.assertEqual(self.PERSON_INSTANCE._title.column_value, "titleCustom")
        self.assertEqual(self.PERSON_INSTANCE._content.column_value, "contentCustom")
        self.assertEqual(self.PERSON_INSTANCE._dni_list.column_value, [1, 2, 3, 4, 5, 6])


if "__main__" == __name__:
    unittest.main()
