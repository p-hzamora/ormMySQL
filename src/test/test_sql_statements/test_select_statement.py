from __future__ import annotations
from typing import Annotated, Callable, Self, Type
import pytest


from ormlambda.dialects import mysql
from test.models import Address, City, Country
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine

from ormlambda import Table, ForeignKey, Column, PrimaryKey, INT, VARCHAR
from pydantic import BaseModel


class TableDB4(Table):
    __table_name__ = "db_4.main_table_4"

    pk_db_4: Annotated[Column[INT], PrimaryKey()]
    data_4: Annotated[Column[VARCHAR], VARCHAR(100)]


class TableDB3(Table):
    __table_name__ = "db_3.main_table_3"

    pk_db_3: Annotated[Column[INT], PrimaryKey()]
    data_3: Annotated[Column[VARCHAR], VARCHAR(100)]
    fk_tbl_4: Column[INT]

    TableDB4 = ForeignKey[Self, TableDB4](TableDB4, lambda i, o: i.fk_tbl_4 == o.pk_db_4)


class TableDB2(Table):
    __table_name__ = "db_2.main_table_2"

    pk_db_2: Annotated[Column[INT], PrimaryKey()]
    data_2: Annotated[Column[VARCHAR], VARCHAR(100)]
    fk_tbl_3: Column[INT]

    TableDB3 = ForeignKey[Self, TableDB3](TableDB3, lambda i, o: i.fk_tbl_3 == o.pk_db_3)


class TableDB1(Table):
    __table_name__ = "db_1.main_table_1"

    pk_db_1: Annotated[Column[INT], PrimaryKey()]
    data_1: Annotated[Column[VARCHAR], VARCHAR(100)]
    fk_tbl_2: Column[INT]

    TableDB2 = ForeignKey[Self, TableDB2](TableDB2, lambda i, o: i.fk_tbl_2 == o.pk_db_2)


DIALECT = mysql.dialect


@pytest.fixture( autouse=True)
def create_db(engine_no_db: Engine):
    ddbb_list = (
        "db_1",
        "db_2",
        "db_3",
        "db_4",
    )

    for db in ddbb_list:
        engine_no_db.create_schema(db, "replace")

    yield

    for db in ddbb_list:
        engine_no_db.drop_schema(db)


@pytest.fixture(autouse=True)
def create_tables(create_engine_for_db):
    engine1 = create_engine_for_db("db_1")
    engine2 = create_engine_for_db("db_2")
    engine3 = create_engine_for_db("db_3")
    engine4 = create_engine_for_db("db_4")
    tables: dict[Type[Table], Callable[[], None]] = {
        TableDB4: populate_table_db4_list,
        TableDB3: populate_table_db3_list,
        TableDB2: populate_table_db2_list,
        TableDB1: populate_table_db1_list,
    }

    engine4 = ORM(TableDB4, engine4)
    engine3 = ORM(TableDB3, engine3)
    engine2 = ORM(TableDB2, engine2)
    engine1 = ORM(TableDB1, engine1)

    engine4.create_table(DIALECT)
    engine3.create_table(DIALECT)
    engine2.create_table(DIALECT)
    engine1.create_table(DIALECT)

    tbl4_list = populate_table_db4_list(3)
    tbl3_list = populate_table_db3_list(tbl4_list)
    tbl2_list = populate_table_db2_list(tbl3_list)
    tbl1_list = populate_table_db1_list(tbl2_list)

    engine4.insert(tbl4_list)
    engine3.insert(tbl3_list)
    engine2.insert(tbl2_list)
    engine1.insert(tbl1_list)

    yield

    for table in tables:
        table.drop_table(DIALECT)


def populate_table_db4_list(n: int) -> list[TableDB4]:
    """Create a list of TableDB4 objects."""
    return [TableDB4(pk_db_4=i, data_4=f"Data_4_{i}") for i in range(1, n + 1)]


def populate_table_db3_list(tbl4_list: list[TableDB4]) -> list[TableDB3]:
    """Create a list of TableDB3 objects linked to TableDB4."""
    return [TableDB3(pk_db_3=i, data_3=f"Data_3_{i}", fk_tbl_4=tbl4.pk_db_4) for i, tbl4 in enumerate(tbl4_list, start=1)]


def populate_table_db2_list(tbl3_list: list[TableDB3]) -> list[TableDB2]:
    """Create a list of TableDB2 objects linked to TableDB3."""
    return [TableDB2(pk_db_2=i, data_2=f"Data_2_{i}", fk_tbl_3=tbl3.pk_db_3) for i, tbl3 in enumerate(tbl3_list, start=1)]


def populate_table_db1_list(tbl2_list: list[TableDB2]) -> list[TableDB1]:
    """Create a list of TableDB1 objects linked to TableDB2."""
    return [TableDB1(pk_db_1=i, data_1=f"Data_1_{i}", fk_tbl_2=tbl2.pk_db_2) for i, tbl2 in enumerate(tbl2_list, start=1)]


@pytest.fixture
def tbl1(create_engine_for_db) -> IStatements[TableDB1]:
    return ORM(TableDB1, create_engine_for_db("db_1"))


def test_select_all(amodel: IStatements[Address]):
    res1 = amodel.select()
    res2 = amodel.select(lambda x: x)
    res3 = amodel.select(lambda x: (x,))

    assert isinstance(res1, tuple)
    assert isinstance(res1[0], Address)
    assert res1 == res2
    assert res2 == res3


def test_select_all_different_tables(amodel: IStatements[Address]):
    res1 = amodel.select(
        lambda x: (
            x,
            x.City,
            x.City.Country,
        ),
        avoid_duplicates=True,
    )

    assert isinstance(res1, tuple)
    assert isinstance(res1[0][0], Address)
    assert isinstance(res1[0][1], City)
    assert isinstance(res1[0][2], Country)

    for a, ci, co in res1:
        assert a.city_id == ci.city_id
        assert ci.country_id == co.country_id


def test_select_tables_from_different_database(tbl1: IStatements[TableDB1]) -> None:
    class Response(BaseModel):
        data_1: str
        data_2: str
        data_3: str
        data_4: str

    res = tbl1.where(lambda x: x.pk_db_1 == 1).first(
        lambda x: (
            x.data_1,
            x.TableDB2.data_2,
            x.TableDB2.TableDB3.data_3,
            x.TableDB2.TableDB3.TableDB4.data_4,
        ),
        flavour=Response,
    )

    assert res == Response(
        data_1="Data_1_1",
        data_2="Data_2_1",
        data_3="Data_3_1",
        data_4="Data_4_1",
    )
