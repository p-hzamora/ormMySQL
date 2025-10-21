from typing import Annotated


from ormlambda import Column  # noqa: E402
from ormlambda import Table  # noqa: E402
from ormlambda.sql.table import TableMeta  # noqa: E402
from ormlambda import JSON, INT, AutoIncrement, PrimaryKey


class Person(Table):
    __table_name__ = "person"

    pk_id: Annotated[None | Column[INT], PrimaryKey(), AutoIncrement()]
    name: Column[str]
    age: Column[int]
    email: Column[str]
    phone: Column[str]
    address: Column[str]


P1 = Person(None, "Pablo", 25, "pablo@icloud.com", "6XXXXXXXXX", "C/ Madrid N_1, 3B")
P2 = Person(None, "Pablo", 25, "pablo@icloud.com", "6XXXXXXXXX", "C/ Madrid N_1, 3B")


class JsonTable(Table):
    __table_name__ = "json_table"

    pk: Column[INT] = Column(INT, is_primary_key=True)
    roles: Column[JSON] = Column(JSON())


def test_initialize_person():
    assert isinstance(P1, Table)


def test_if_two_objects_are_equals():
    assert P1 == P2


def test_if_two_objects_are_not_the_same():
    assert P1 is not P2


def test_if_Person_is_subclass_of_Table():
    assert issubclass(Person, Table)


def test_if_instance_of_person_is_subclass_of_Table():
    assert isinstance(P1, Table)


def test_Person_is_type_of_TableMeta():
    assert type(Table) == TableMeta


def test_TableMeta_type_is_type():
    assert type(TableMeta) == type


def test_hashable_table() -> None:
    user = JsonTable(
        pk=1,
        roles=[1, 2, 3, 4, {1: "one", 2: "two", 3: "three", 4: "four"}, [1, 2, 3, [4, 4, 4, [5, 5, 5, 5, 5]]]],
    )

    user2 = JsonTable(
        pk=1,
        roles=[1, 2, 3, 4, {1: "one", 2: "two", 3: "three", 4: "four"}, [1, 2, 3, [4, 4, 4, [5, 5, 5, 5, 5]]]],
    )

    assert user == user2
