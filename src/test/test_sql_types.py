import sys
from pathlib import Path
import unittest
from parameterized import parameterized


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Column, Table, create_engine, ORM
from ormlambda.sql.type_api import TypeEngine
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


def url_creator(db: str = ""):
    return f"mysql://root:1500@localhost:3306{f'/{db}' if db else ''}?pool_size=3"


def create_engine_for_db(db: str = ""):
    URL = url_creator(db)
    return create_engine(URL)


class TestDataType(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        TEST_DB = "__test_create_schema__"
        engine = create_engine_for_db(TEST_DB)
        engine.drop_schema(TEST_DB)

    @parameterized.expand(
        [
            (int_type, "INTEGER"),
            (string_type, "VARCHAR(100)"),
            (char_type, "CHAR(10)"),
            (text_type, "TEXT"),
            (datetime_type, "DATETIME"),
            (timestamp_type, "TIMESTAMP(6)"),
            (bool_type, "BOOL"),
        ]
    )
    def test_types_mysql(self, type_: TypeEngine, result: str) -> None:
        engine = create_engine_for_db()
        TEST_DB = "__test_create_schema__"

        engine.create_schema(TEST_DB, "replace")
        engine_test_db = create_engine_for_db(TEST_DB)
        self.assertEqual(engine_test_db.dialect.type_compiler_instance.process(type_), result)


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


class TestTypes(unittest.TestCase):
    def test_create_table(self):
        engine = create_engine_for_db()
        TEST_DB = "__test_create_schema__"

        engine.create_schema(TEST_DB)
        engine_test_db = create_engine_for_db(TEST_DB)
        ORM(TableType, engine_test_db).create_table("replace")


if __name__ == "__main__":
    unittest.main()
