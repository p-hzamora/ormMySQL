from typing import Generator
from ormlambda import Column, Table, Engine, ORM
from ormlambda.sql.type_api import TypeEngine
import pytest
from ormlambda.dialects.mysql import (
    CHAR,
    TEXT,
    DATETIME,
    TIMESTAMP,
    BOOLEAN,
    VARCHAR,
    INTEGER,
    FLOAT,
    POINT,
    DATE,
    DECIMAL,
)

from ormlambda.dialects import mysql

DIALECT = mysql.dialect
# Create some SQL types
int_type = INTEGER
string_type = VARCHAR(length=100)
char_type = CHAR(length=10)
text_type = TEXT
datetime_type = DATETIME
timestamp_type = TIMESTAMP(timezone=True, fsp=6)
bool_type = BOOLEAN


type ColumnCustom[T] = Column[T]


class TableType(Table):
    __table_name__ = "table_type"

    pk: Column[INTEGER] = Column(INTEGER(), is_primary_key=True, is_auto_increment=False)
    strings: Column[VARCHAR] = Column(VARCHAR(255))
    integers: Column[INTEGER] = Column(INTEGER())
    floats: Column[FLOAT] = Column(FLOAT())
    points: Column[POINT] = Column(POINT())
    datetimes: Column[DATETIME] = Column(DATETIME())
    dates: Column[DATE] = Column(DATE())
    decimals: Column[DECIMAL] = Column(DECIMAL(precision=5, scale=2))


@pytest.fixture(autouse=True)
def engine(engine_no_db, create_engine_for_db) -> Generator[Engine, None, None]:
    TEST_DB = "__test_create_schema__"

    engine_no_db.create_schema(TEST_DB, "replace")

    engine: Engine = create_engine_for_db(TEST_DB)

    yield engine
    engine.drop_schema(TEST_DB)


@pytest.mark.parametrize(
    "type_,result",
    [
        (int_type, "INTEGER"),
        (string_type, "VARCHAR(100)"),
        (char_type, "CHAR(10)"),
        (text_type, "TEXT"),
        (datetime_type, "DATETIME"),
        (timestamp_type, "TIMESTAMP(6)"),
        (bool_type, "BOOL"),
    ],
)
def test_types_mysql(engine: Engine, type_: TypeEngine, result: str) -> None:
    assert engine.dialect.type_compiler_instance.process(type_) == result


def test_create_table(engine):
    ORM(TableType, engine).create_table("replace")
