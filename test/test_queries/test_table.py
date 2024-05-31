import unittest

from orm.orm_objects import Table, Column
from typing import get_type_hints

from orm.orm_objects.table.table_constructor import __init_constructor__, Base


@__init_constructor__
class PetDecorator:
    name: Column[str] = Column[str](is_primary_key=True)
    age: Column[int] = Column[int]()
    sound: Column[str] = Column[str]()


class PetHeritage(Base):
    name: Column[str] = Column[str](is_primary_key=True)
    age: Column[int] = Column[int]()
    sound: Column[str] = Column[str]()


class PersonInit:
    def __init__(self, age: int, name: str) -> None:
        self._age: Column[int] = Column[int]("age", age, is_auto_increment=True)
        self._name: Column[str] = Column[str]("name", name)

    @property
    def age(self) -> int:
        return self._age.column_value

    @age.setter
    def age(self, value: int) -> int:
        self._age.column_value = value

    @property
    def name(self) -> str:
        return self._name.column_value

    @name.setter
    def name(self, value: str) -> str:
        self._name.column_value = value


class Person(Table):
    age: Column[int] = Column[int](is_auto_increment=True)
    name: Column[str] = Column[str]()


class TestTableConstructor(unittest.TestCase):
    PERSON = Person(25, "pablo")

    def test_constructor(self):
        self.assertEqual(self.PERSON._age.column_value, 25)
        self.assertEqual(self.PERSON._age.is_primary_key, False)
        self.assertEqual(self.PERSON._age.is_auto_increment, True)
        self.assertEqual(self.PERSON._name.column_value, "pablo")

        self.assertIsInstance(self.PERSON._age, Column)
        self.assertIsInstance(self.PERSON._name, Column)

        self.assertEqual(self.PERSON.age, 25)
        self.assertEqual(self.PERSON.name, "pablo")

    def test_update_property(self):
        self.assertEqual(self.PERSON.age, 25)
        self.assertEqual(self.PERSON.name, "pablo")

        self.PERSON.age = 10
        self.PERSON.name = "marcos"
        self.assertEqual(self.PERSON.age, 10)
        self.assertEqual(self.PERSON.name, "marcos")
        self.assertEqual(self.PERSON._age.column_value, 10)
        self.assertEqual(self.PERSON._name.column_value, "marcos")


class TestCustomDataclass(unittest.TestCase):
    def test___init__creation(self):
        self.assertTrue(hasattr(PetDecorator, "__init__"))
        self.assertEqual(
            get_type_hints(PetDecorator),
            {"age": Column[int], "name": Column[str], "sound": Column[str]},
        )

    def __check_properties(self, obj: PetDecorator | PetHeritage):
        self.assertEqual(obj.name.column_value, "fido")
        self.assertEqual(obj.age.column_value, 3)
        self.assertEqual(obj.sound.column_value, "woof")

    def test_check_that_properties_were_assigned(self):
        self.__check_properties(PetDecorator("fido", 3))
        self.__check_properties(PetHeritage("fido", 3))

    def __check_if_default_can_be_overridden(self, obj: PetDecorator | PetHeritage):
        self.assertEqual(obj.name.column_value, "rover")
        self.assertEqual(obj.age.column_value, 5)
        self.assertEqual(obj.sound.column_value, "bark")

    def test_check_that_the_default_can_be_overridden(self):
        self.__check_if_default_can_be_overridden(PetDecorator("rover", 5, "bark"))
        self.__check_if_default_can_be_overridden(PetHeritage("rover", 5, "bark"))


if __name__ == "__main__":
    unittest.main()
