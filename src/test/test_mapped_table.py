from typing import Annotated

from parameterized import parameterized
import pytest

from ormlambda import Table, Column, INT, VARCHAR, JSON  # noqa: E402
from ormlambda import PrimaryKey, ORM


class Person(Table):
    __table_name__ = "person"

    id: Annotated[Column[INT], PrimaryKey()]
    title: Column[VARCHAR]
    content: Column[VARCHAR]
    dni_list: Column[JSON]


@pytest.fixture
def person():
    return Person(1, "titleCustom", "contentCustom", [1, 2, 3, 4, 5, 6])


def test_create_orm(person: Person):
    assert person.id == 1
    assert person.title == "titleCustom"
    assert person.content == "contentCustom"
    assert person.dni_list == [1, 2, 3, 4, 5, 6]


def test_column_name():
    assert Person.id.column_name == "id"
    assert Person.title.column_name == "title"
    assert Person.content.column_name == "content"
    assert Person.dni_list.column_name == "dni_list"


def test_column_value(person: Person):
    assert person.id == 1
    assert person.title == "titleCustom"
    assert person.content == "contentCustom"
    assert person.dni_list == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize(
    "attrs,mssg",
    [
        ({"id": "should be <int>"}, "The 'id' Column from 'person' table, expected 'INTEGER' type. You passed 'str' type"),
        ({"title": 1}, "The 'title' Column from 'person' table, expected 'VARCHAR' type. You passed 'int' type"),
        ({"content": 1}, "The 'content' Column from 'person' table, expected 'VARCHAR' type. You passed 'int' type"),
        ({"dni_list": "should be <dict>"}, "The 'dni_list' Column from 'person' table, expected 'JSON' type. You passed 'str' type"),
    ],
)
def test_raise_ValueError(attrs, mssg):
    with pytest.raises(ValueError) as error:
        Person(**attrs)
    assert str(error.value) == mssg
