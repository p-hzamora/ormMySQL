import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from orm import Table, Column
from orm import nameof


class Person(Table):
    __table_name__ = "person"

    def __init__(
        self,
        id: int,
        title: int,
        content: int,
        dni_list: list,
    ) -> None:
        self._id: Column[int] = Column(nameof(id), id, is_primary_key=True)
        self._title: Column[int] = Column(nameof(title), title)
        self._content: Column[int] = Column(nameof(content), content)
        self._dni_list: Column[list] = Column(nameof(dni_list), str(dni_list))

    @property
    def id(self):
        return self._id.column_value

    @id.setter
    def id(self, value):
        self._id.column_value = value

    @property
    def title(self):
        return self._title.column_value

    @title.setter
    def title(self, value):
        self._title.column_value = value

    @property
    def content(self):
        return self._content.column_value

    @content.setter
    def content(self, value):
        self._content.column_value = value

    @property
    def dni_list(self):
        return eval(self._dni_list.column_value)

    @dni_list.setter
    def dni_list(self, value):
        self._dni_list.column_value = str(value)


class TestSQLMapping(unittest.TestCase):
    PERSON_INSTANCE: Person = Person(1, "titleCustom", "contentCustom", [1, 2, 3, 4, 5, 6])

    def __init__(self, methodName: str = "SQLMapping") -> None:
        super().__init__(methodName)

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
        self.assertEqual(self.PERSON_INSTANCE._dni_list.column_value, "[1, 2, 3, 4, 5, 6]")


if "__main__" == __name__:
    unittest.main()
