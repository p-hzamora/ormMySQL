import sys
from pathlib import Path
import unittest

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects import Table, Column  # noqa: E402
from typing import Type, get_type_hints  # noqa: E402

from orm.orm_objects.table.table_constructor import __init_constructor__  # noqa: E402


@__init_constructor__
class PetDecorator:
    name: str = Column[str](is_unique=True)
    age: int = Column[int](is_auto_increment=True)
    sound: str
    id_pet: int = Column[int](is_primary_key=True)


class PetHeritage(Table):
    name: str = Column[str](is_unique=True)
    age: int = Column[int](is_auto_increment=True)
    sound: str
    id_pet: int = Column[int](is_primary_key=True)


class PetInit:
    def __init__(
        self,
        name: str = None,
        age: int = None,
        sound: str = None,
        id_pet: int = None,
    ) -> None:
        self._name: str = Column[str]("name", name)
        self._age: int = Column[int]("age", age, is_auto_increment=True)
        self._sound: str = Column[str]("sound", sound)
        self._id_pet: int = Column[int]("id_pet", id_pet, is_primary_key=True)

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


TypePet = PetDecorator | PetHeritage | PetInit


class TestTableConstructor(unittest.TestCase):
    PetClasses: tuple[Type[TypePet]] = (
        PetDecorator,
        PetHeritage,
        PetInit,
    )

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def _test_constructor(self, obj: TypePet):
        self.assertEqual(obj._age.column_value, 25)
        self.assertEqual(obj._age.is_primary_key, False)
        self.assertEqual(obj._age.is_auto_increment, True)
        self.assertEqual(obj._name.column_value, "pablo")

        self.assertIsInstance(obj._age, Column)
        self.assertIsInstance(obj._name, Column)

        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.name, "pablo")

    def _test_update_property(self, obj: TypePet):
        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.name, "pablo")

        obj.age = 10
        obj.name = "marcos"
        self.assertEqual(obj.age, 10)
        self.assertEqual(obj.name, "marcos")
        self.assertEqual(obj._age.column_value, 10)
        self.assertEqual(obj._name.column_value, "marcos")

    def _test_column_class_values(self, obj:TypePet):
        self.assertEqual(obj._name.is_primary_key,False)
        self.assertEqual(obj._name.is_auto_generated,False)
        self.assertEqual(obj._name.is_auto_increment,False)
        self.assertEqual(obj._name.is_unique,True)




_age.is_primary_key
_age.is_auto_generated
_age.is_auto_increment
_age.is_unique

.is_primary_key
.is_auto_generated
.is_auto_increment
.is_unique

.is_primary_key
.is_auto_generated
.is_auto_increment
.is_unique

.is_primary_key
.is_auto_generated
.is_auto_increment
.is_unique



    def test_TableConstructor(self):
        for pet_class in self.PetClasses:
            instance = pet_class("pablo", 25)
            self._test_constructor(instance)
            self._test_update_property(instance)


class TestCustomDataclass(unittest.TestCase):
    def test___init__creation(self):
        self.assertTrue(hasattr(PetDecorator, "__init__"))
        self.assertEqual(
            get_type_hints(PetDecorator),
            {
                "name": Column[str],
                "age": Column[int],
                "sound": Column[str],
                "id_pet": Column[int],
            },
        )

    def test_check_that_properties_were_assigned(self):
        self.__check_properties(PetDecorator("fido", 3))
        self.__check_properties(PetHeritage("fido", 3))

    def __check_properties(self, obj: PetDecorator | PetHeritage):
        self.assertEqual(obj.name, "fido")
        self.assertEqual(obj.age, 3)
        self.assertEqual(obj.sound, None)

    def test_check_that_the_default_can_be_overridden(self):
        self.__check_if_default_can_be_overridden(PetDecorator("rover", 5, "bark"))
        self.__check_if_default_can_be_overridden(PetHeritage("rover", 5, "bark"))

    def __check_if_default_can_be_overridden(self, obj: PetDecorator | PetHeritage):
        self.assertEqual(obj.name, "rover")
        self.assertEqual(obj.age, 5)
        self.assertEqual(obj.sound, "bark")


if __name__ == "__main__":
    unittest.main()
