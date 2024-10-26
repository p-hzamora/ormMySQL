from __future__ import annotations
import sys
from pathlib import Path
import unittest
from typing import get_type_hints, Self, Type
from parameterized import parameterized

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.utils import ForeignKey, Table, Column  # noqa: E402
from ormlambda.utils.table_constructor import __init_constructor__  # noqa: E402
from models import City  # noqa: E402


@__init_constructor__
class PersonDecorator:
    __table_name__ = "person"
    name: str = Column[str](is_unique=True)
    age: int = Column[int](is_auto_increment=True)
    sound: str
    id_person: int = Column[int](is_primary_key=True)
    fk_city: int

    city = ForeignKey[Self, City](__table_name__, City, lambda p, c: p.fk_city == c.city_id)


class PersonInherit(Table):
    __table_name__ = "person"
    name: str = Column[str](is_unique=True)
    age: int = Column[int](is_auto_increment=True)
    sound: str
    id_person: int = Column[int](is_primary_key=True)
    fk_city: int

    city = ForeignKey[Self, City](__table_name__, City, lambda p, c: p.fk_city == c.city_id)


class PersonInit:
    # we don't added type-hint because this class hasn't the hability to deleted special variables from __annotations__ and failed in '_test_type_hints'
    __table_name__ = "person"

    def __init__(
        self,
        name: str = None,
        age: int = None,
        sound: str = None,
        id_person: int = None,
        fk_city: int = None,
    ) -> None:
        self._name: Column[str] = Column[str](dtype=str, column_name="name", column_value=name, is_unique=True)
        self._age: Column[int] = Column[int](dtype=int, column_name="age", column_value=age, is_auto_increment=True)
        self._sound: Column[str] = Column[str](dtype=str, column_name="sound", column_value=sound)
        self._id_person: Column[int] = Column[int](dtype=int, column_name="id_person", column_value=id_person, is_primary_key=True)
        self._fk_city: Column[int] = Column[int](dtype=int, column_name="fk_city", column_value=fk_city)

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

    @property
    def sound(self) -> int:
        return self._sound.column_value

    @sound.setter
    def sound(self, value: int) -> int:
        self._sound.column_value = value

    @property
    def id_person(self) -> str:
        return self._id_person.column_value

    @id_person.setter
    def id_person(self, value: str) -> str:
        self._id_person.column_value = value

    @property
    def fk_city(self) -> str:
        return self._fk_city.column_value

    @fk_city.setter
    def fk_city(self, value: str) -> str:
        self._fk_city.column_value = value


TypePerson = PersonDecorator | PersonInherit | PersonInit
ThreeDifferentPersonClasses: list[TypePerson] = [
    PersonDecorator,
    PersonInherit,
    PersonInit,
]


class TestTableConstructor(unittest.TestCase):
    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_constructor(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance._age.column_value, 25)
        self.assertEqual(instance._age.is_primary_key, False)
        self.assertEqual(instance._age.is_auto_increment, True)
        self.assertEqual(instance._name.column_value, "pablo")

        self.assertEqual(instance._sound.column_value, None)
        self.assertEqual(instance._id_person.column_value, None)

        self.assertIsInstance(instance._age, Column)
        self.assertIsInstance(instance._name, Column)

        self.assertEqual(instance.age, 25)
        self.assertEqual(instance.name, "pablo")

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_update_property(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance.age, 25)
        self.assertEqual(instance.name, "pablo")

        instance.age = 10
        instance.name = "marcos"
        self.assertEqual(instance.age, 10)
        self.assertEqual(instance.name, "marcos")
        self.assertEqual(instance._age.column_value, 10)
        self.assertEqual(instance._name.column_value, "marcos")

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_column_class_name(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance._name.is_primary_key, False)
        self.assertEqual(instance._name.is_auto_generated, False)
        self.assertEqual(instance._name.is_auto_increment, False)
        self.assertEqual(instance._name.is_unique, True)

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_column_class_age(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance._age.is_primary_key, False)
        self.assertEqual(instance._age.is_auto_generated, False)
        self.assertEqual(instance._age.is_auto_increment, True)
        self.assertEqual(instance._age.is_unique, False)

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_column_class_sound(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance._sound.is_primary_key, False)
        self.assertEqual(instance._sound.is_auto_generated, False)
        self.assertEqual(instance._sound.is_auto_increment, False)
        self.assertEqual(instance._sound.is_unique, False)

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_column_class_id_person(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertEqual(instance._id_person.is_primary_key, True)
        self.assertEqual(instance._id_person.is_auto_generated, False)
        self.assertEqual(instance._id_person.is_auto_increment, False)
        self.assertEqual(instance._id_person.is_unique, False)

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test___init__creation(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertTrue(hasattr(instance, "__init__"))

    @parameterized.expand(ThreeDifferentPersonClasses)
    def test_properties_creation(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        self.assertIsInstance(instance.__class__.name, property)
        self.assertIsInstance(instance.__class__.age, property)
        self.assertIsInstance(instance.__class__.sound, property)
        self.assertIsInstance(instance.__class__.id_person, property)

    @parameterized.expand(
        [
            PersonDecorator,
            PersonInherit,
            # PersonInit, # COMMENT: cannot use type_hints in when creating class with __init__
        ]
    )
    def test_type_hints(self, obj: Type[TypePerson]):
        instance = obj("pablo", 25)
        dicc = {
            "name": Column[str](dtype=str, is_unique=True),
            "age": Column[int](dtype=int, is_auto_increment=True),
            "sound": Column[str](dtype=str),
            "id_person": Column[int](dtype=int, is_primary_key=True),
            "fk_city": Column[int](dtype=int),
        }
        self.assertDictEqual(get_type_hints(instance), dicc)


if __name__ == "__main__":
    unittest.main()
