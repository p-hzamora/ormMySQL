from typing import Annotated, Optional

from ormlambda import Table, Column, ORM, IStatements
from ormlambda import CheckTypes, PrimaryKey
from ormlambda.engine import Engine
from ormlambda.sql.sqltypes import LargeBinary as Binary, INTEGER

from test.models import Address, City, Country  # noqa: E402


def test_SELECT_method_passing_3_columns(amodel: IStatements[Address]):
    response = amodel.select(
        lambda a: (
            a,
            a.City,
            a.City.Country,
        ),
        avoid_duplicates=True,
    )
    for a, city, country in response:
        assert isinstance(response, tuple)
        assert isinstance(a, Address)
        assert isinstance(city, City)
        assert isinstance(country, Country)


def test_SELECT_method_passing_1_column(amodel: IStatements[Address]):
    response = amodel.select(lambda a: (a.City,))
    assert isinstance(response, tuple)
    assert isinstance(response[0], City)


def test_SELECT_ONE_method_passing_0_column(amodel: IStatements[Address]):
    response = amodel.select_one()
    assert isinstance(response, Address)


def test_SELECT_ONE_method_passing_tuple_with_table_it(amodel: IStatements[Address]):
    response = amodel.select_one(lambda x: (x,))
    assert isinstance(response, Address)


def test_SELECT_ONE_method_passing_the_same_table_it(amodel: IStatements[Address]):
    response = amodel.select_one(lambda x: x)
    assert isinstance(response, Address)


def test_SELECT_ONE_method_passing_3_columns_of_the_same_table(amodel: IStatements[Address]):
    response = amodel.select_one(lambda x: (x.address, x.address2, x.city_id), flavour=tuple)
    assert isinstance(response, tuple)
    assert isinstance(response[0], str)
    assert isinstance(response[1], Optional[str])
    assert isinstance(response[2], int)


def test_SELECT_ONE_method_passing_3_columns(amodel: IStatements[Address]):
    response = amodel.select_one(
        lambda a: (
            a,
            a.City,
            a.City.Country,
        ),
        avoid_duplicates=True,
    )
    a, city, country = response
    assert isinstance(response, tuple)
    assert isinstance(a, Address)
    assert isinstance(city, City)
    assert isinstance(country, Country)


def test_SELECT_ONE_method_passing_1_column(amodel: IStatements[Address]):
    response = amodel.select_one(lambda a: (a,))

    assert isinstance(response, Address)
    assert isinstance(response.address, str)


def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_DICT(amodel: IStatements[Address]):
    response = amodel.select_one(lambda a: (a,), flavour=dict)
    assert isinstance(response, dict)
    assert isinstance(list(response.values())[0], int)


def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_TUPLE(amodel: IStatements[Address]):
    response = amodel.select_one(lambda a: (a,), flavour=tuple)
    assert isinstance(response, tuple)
    assert isinstance(response[0], int)


def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_LIST(amodel: IStatements[Address]):
    response = amodel.select_one(lambda a: (a,), flavour=list)
    assert isinstance(response, list)
    assert isinstance(response[0], int)


def test_SELECT_ONE_method_with_SET_as_flavour_newer_module(amodel: IStatements[Address]):
    # COMMENT: if we used 'mysql-connector', the BLOB data will be returned as a 'bytearray' (an unhashable data type). However, if you use the newer 'mysql-connector-python' you'll retrieve 'bytes' which are hashable
    selection = amodel.select_one(lambda a: (a,), flavour=set)
    assert len(selection) == 8


def test_SELECT_ONE_method_with_SET_as_flavour_and_avoid_raises_TypeError(sakila_engine: Engine, create_engine_for_db):  # noqa: F811
    class TableWithBytearray(Table):
        __table_name__ = "bytearray_table"
        pk: Annotated[int, INTEGER(), PrimaryKey()]
        byte_data: Annotated[Column[Binary], CheckTypes(False)]

    DDBB_NAME: str = "__TEST_DATABASE__"

    sakila_engine.create_schema(DDBB_NAME, "replace")

    new_engine = create_engine_for_db(DDBB_NAME)

    byte_model = ORM(TableWithBytearray, new_engine)
    byte_model.create_table()

    # COMMENT: if we used 'mysql-connector', the BLOB data will be returned as a 'bytearray' (an unhashable data type). However, if you use the newer 'mysql-connector-python' you'll retrieve 'bytes' which are hashable
    BYTE_DATA = bytes(b"bytearray data")
    SET_BYTE_DATA = {BYTE_DATA}

    byte_model.insert(TableWithBytearray(1, BYTE_DATA))
    res = byte_model.first(lambda x: x.byte_data, flavour=set)

    assert res == SET_BYTE_DATA
    new_engine.drop_schema(DDBB_NAME)
