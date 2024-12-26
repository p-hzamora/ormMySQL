from __future__ import annotations
import sys
from pathlib import Path
import unittest
from typing import Self, Type, Optional
from parameterized import parameterized

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.utils import ForeignKey, Table, Column  # noqa: E402
from ormlambda.utils.table_constructor import __init_constructor__
from models import City  # noqa: E402


class PersonInherit(Table):
    __table_name__ = "person"
    name: Column[str] = Column(str, is_unique=True)
    age: Column[int] = Column(int, is_auto_increment=True)
    sound: Column[str]
    id_person: Column[int] = Column(int, is_primary_key=True)
    fk_city: Column[int]

    city = ForeignKey[Self, City](City, lambda p, c: p.fk_city == c.city_id)


@__init_constructor__
class PersonDecorator:
    __table_name__ = "person"
    name: Column[str] = Column(str, is_unique=True)
    age: Column[int] = Column(int, is_auto_increment=True)
    sound: Column[str]
    id_person: Column[int] = Column(int, is_primary_key=True)
    fk_city: Column[int]

    city = ForeignKey[Self, City](City, lambda p, c: p.fk_city == c.city_id)


class PersonInit:
    # we don't added type-hint because this class hasn't the hability to deleted special variables from __annotations__ and failed in '_test_type_hints'
    __table_name__ = "person"

    name: Column[str] = Column(str, is_unique=True)
    age: Column[int] = Column(int, is_auto_increment=True)
    sound: Column[str] = Column(str)
    id_person: Column[int] = Column(int, is_primary_key=True)
    fk_city: Column[int] = Column(int)

    city = ForeignKey[Self, City](City, lambda p, c: p.fk_city == c.city_id)

    def __init__(
        self,
        name: Column[str] = None,
        age: Column[int] = None,
        sound: Column[str] = None,
        id_person: Column[int] = None,
        fk_city: Column[int] = None,
    ) -> None:
        self.name: Column[str] = name
        self.age: Column[int] = age
        self.sound: Column[str] = sound
        self.id_person: Column[int] = id_person
        self.fk_city: Column[int] = fk_city


type PersonType = Type[PersonInherit] | Type[PersonDecorator] | Type[PersonInit]
PersonClasses = (PersonInherit, PersonDecorator, PersonInit)


class TestTableConstructor(unittest.TestCase):
    @parameterized.expand(PersonClasses)
    def test_constructor(self, obj: PersonType):
        instance = obj("pablo", 25)

        instance.age

    @parameterized.expand(PersonClasses)
    def test_column_data_descriptor_in_class(self, _class: PersonType) -> None:
        self.assertIsInstance(_class.name, Column)
        self.assertIsInstance(_class.age, Column)
        self.assertIsInstance(_class.sound, Column)
        self.assertIsInstance(_class.id_person, Column)
        self.assertIsInstance(_class.fk_city, Column)

    @parameterized.expand(PersonClasses)
    def test_column_attributes(self, _class: PersonType) -> None:
        self.assertIsInstance(_class.name, Column)
        self.assertIsInstance(_class.age, Column)
        self.assertIsInstance(_class.sound, Column)
        self.assertIsInstance(_class.id_person, Column)
        self.assertIsInstance(_class.fk_city, Column)

    @parameterized.expand(PersonClasses)
    def test_column_data_descriptor_in_object(self, _class: PersonType) -> None:
        obj = _class("pablo", 25, "aggr", 1)
        self.assertIsInstance(obj.name, Optional[str])
        self.assertIsInstance(obj.age, Optional[int])
        self.assertIsInstance(obj.sound, Optional[str])
        self.assertIsInstance(obj.id_person, Optional[int])
        self.assertIsInstance(obj.fk_city, Optional[int])

    @parameterized.expand(PersonClasses)
    def test_fk_descriptor_in_class(self, _class: PersonType) -> None:
        self.assertIsInstance(_class.city, ForeignKey)

    @parameterized.expand(PersonClasses)
    def test_fk_descriptor_in_object(self, _class: PersonType) -> None:
        obj = _class("pablo", 25, "aggr", 1)
        self.assertIs(obj.city, City)

    @parameterized.expand(PersonClasses)
    def test_values(self, _class: PersonType) -> None:
        obj = _class("pablo", 25, "aggr", 1)
        self.assertEqual(obj.name, "pablo")
        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.sound, "aggr")
        self.assertEqual(obj.id_person, 1)
        self.assertEqual(obj.fk_city, None)

    @parameterized.expand(PersonClasses)
    def test_raiseError_while_setting_fk(self, _class: PersonType) -> None:
        with self.assertRaises(AttributeError) as err:
            obj = _class("Pablo", 25)
            obj.city = "new_value"

        mssg: str = "The ForeignKey 'city' in the 'person' table cannot be overwritten."
        self.assertEqual(err.exception.args[0], mssg)

    @parameterized.expand(PersonClasses)
    def test_assign_values(self, _class: PersonType) -> None:
        person = _class("pablo", 25, "grrr", 1, 87)

        self.assertEqual(person.name, "pablo")
        self.assertEqual(person.age, 25)
        self.assertEqual(person.sound, "grrr")
        self.assertEqual(person.id_person, 1)
        self.assertEqual(person.fk_city, 87)

        person.name = "new_value"
        person.age = 30
        person.sound = "aaa"
        person.id_person = 20
        person.fk_city = 5

        self.assertEqual(person.name, "new_value")
        self.assertEqual(person.age, 30)
        self.assertEqual(person.sound, "aaa")
        self.assertEqual(person.id_person, 20)
        self.assertEqual(person.fk_city, 5)

    @parameterized.expand(PersonClasses)
    def test_column_class_name(self, _class: PersonType):
        self.assertEqual(_class.name.is_primary_key, False)
        self.assertEqual(_class.name.is_auto_generated, False)
        self.assertEqual(_class.name.is_auto_increment, False)
        self.assertEqual(_class.name.is_unique, True)

    @parameterized.expand(PersonClasses)
    def test_column_class_age(self, _class: PersonType):
        self.assertEqual(_class.age.is_primary_key, False)
        self.assertEqual(_class.age.is_auto_generated, False)
        self.assertEqual(_class.age.is_auto_increment, True)
        self.assertEqual(_class.age.is_unique, False)

    @parameterized.expand(PersonClasses)
    def test_column_class_sound(self, _class: PersonType):
        self.assertEqual(_class.sound.is_primary_key, False)
        self.assertEqual(_class.sound.is_auto_generated, False)
        self.assertEqual(_class.sound.is_auto_increment, False)
        self.assertEqual(_class.sound.is_unique, False)

    @parameterized.expand(PersonClasses)
    def test_column_class_id_person(self, _class: PersonType):
        self.assertEqual(_class.id_person.is_primary_key, True)
        self.assertEqual(_class.id_person.is_auto_generated, False)
        self.assertEqual(_class.id_person.is_auto_increment, False)
        self.assertEqual(_class.id_person.is_unique, False)


if __name__ == "__main__":
    unittest.main()
