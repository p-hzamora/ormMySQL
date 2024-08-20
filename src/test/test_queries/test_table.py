import sys
from pathlib import Path
import unittest

from typing import Type, get_type_hints, Self

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.ormmysql.utils import ForeignKey, Table, Column  # noqa: E402
from src.ormmysql.utils.table_constructor import __init_constructor__  # noqa: E402
from src.test.models import City  # noqa: E402


@__init_constructor__
class PersonDecorator:
    __table_name__ = "person"
    name: str = Column[str](is_unique=True)
    age: int = Column[int](is_auto_increment=True)
    sound: str
    id_person: int = Column[int](is_primary_key=True)
    fk_city: int

    city = ForeignKey[Self, City](__table_name__, City, lambda p, c: p.fk_city == c.city_id)


class PersonHeritage(Table):
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

    name: Column[str]
    age: Column[int]
    sound: Column[str]
    id_person: Column[int]
    fk_city: Column[int]

    city = ForeignKey[Self, City](__table_name__, City, lambda p, c: p.fk_city == c.city_id)

    def __init__(
        self,
        name: str = None,
        age: int = None,
        sound: str = None,
        id_person: int = None,
    ) -> None:
        self._name: Column[str] = Column[str](dtype=str, column_name="name", column_value=name, is_unique=True)
        self._age: Column[int] = Column[int](dtype=int, column_name="age", column_value=age, is_auto_increment=True)
        self._sound: Column[str] = Column[str](dtype=str, column_name="sound", column_value=sound)
        self._id_person: Column[int] = Column[int](dtype=int, column_name="id_person", column_value=id_person, is_primary_key=True)

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


TypePerson = PersonDecorator | PersonHeritage | PersonInit


class TestTableConstructor(unittest.TestCase):
    PersonClasses: tuple[Type[TypePerson]] = (
        PersonDecorator,
        PersonHeritage,
        PersonInit,
    )

    def _test_constructor(self, obj: TypePerson):
        self.assertEqual(obj._age.column_value, 25)
        self.assertEqual(obj._age.is_primary_key, False)
        self.assertEqual(obj._age.is_auto_increment, True)
        self.assertEqual(obj._name.column_value, "pablo")

        self.assertEqual(obj._sound.column_value, None)
        self.assertEqual(obj._id_person.column_value, None)

        self.assertIsInstance(obj._age, Column)
        self.assertIsInstance(obj._name, Column)

        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.name, "pablo")

    def _test_update_property(self, obj: TypePerson):
        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.name, "pablo")

        obj.age = 10
        obj.name = "marcos"
        self.assertEqual(obj.age, 10)
        self.assertEqual(obj.name, "marcos")
        self.assertEqual(obj._age.column_value, 10)
        self.assertEqual(obj._name.column_value, "marcos")

    def _test_column_class_name(self, obj: TypePerson):
        self.assertEqual(obj._name.is_primary_key, False)
        self.assertEqual(obj._name.is_auto_generated, False)
        self.assertEqual(obj._name.is_auto_increment, False)
        self.assertEqual(obj._name.is_unique, True)

    def _test_column_class_age(self, obj: TypePerson):
        self.assertEqual(obj._age.is_primary_key, False)
        self.assertEqual(obj._age.is_auto_generated, False)
        self.assertEqual(obj._age.is_auto_increment, True)
        self.assertEqual(obj._age.is_unique, False)

    def _test_column_class_sound(self, obj: TypePerson):
        self.assertEqual(obj._sound.is_primary_key, False)
        self.assertEqual(obj._sound.is_auto_generated, False)
        self.assertEqual(obj._sound.is_auto_increment, False)
        self.assertEqual(obj._sound.is_unique, False)

    def _test_column_class_id_person(self, obj: TypePerson):
        self.assertEqual(obj._id_person.is_primary_key, True)
        self.assertEqual(obj._id_person.is_auto_generated, False)
        self.assertEqual(obj._id_person.is_auto_increment, False)
        self.assertEqual(obj._id_person.is_unique, False)

    def _test___init__creation(self, obj: TypePerson):
        self.assertTrue(hasattr(obj, "__init__"))

    def _test_properties_creation(self, obj: TypePerson):
        self.assertIsInstance(obj.__class__.name, property)
        self.assertIsInstance(obj.__class__.age, property)
        self.assertIsInstance(obj.__class__.sound, property)
        self.assertIsInstance(obj.__class__.id_person, property)

    def _test_type_hints(self, obj: TypePerson):
        self.assertEqual(
            get_type_hints(obj),
            {
                "name": Column[str],
                "age": Column[int],
                "sound": Column[str],
                "id_person": Column[int],
                "fk_city": Column[int],
            },
        )

    def test_TableConstructor(self):
        """
        I iterate through 3 differente classes, "PersonDecorator" "PersonHeritage" "PersonInit" to make sure I get the same result
        """
        for person_class in self.PersonClasses:
            instance = person_class("pablo", 25)
            self._test_constructor(instance)
            self._test_update_property(instance)
            self._test_column_class_name(instance)
            self._test_column_class_age(instance)
            self._test_column_class_sound(instance)
            self._test_column_class_id_person(instance)
            self._test___init__creation(instance)
            self._test_properties_creation(instance)
            self._test_type_hints(instance)


if __name__ == "__main__":
    unittest.main()
