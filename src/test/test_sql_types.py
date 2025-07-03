import sys
from pathlib import Path
import unittest
from ormlambda.sql.type_api import TypeEngine
from parameterized import parameterized


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Table, Column
from ormlambda import (
    STRING,
    CHAR,
    TEXT,
    DATETIME,
    TIMESTAMP,
    BOOLEAN,
    VARCHAR,
    INT,
    FLOAT,
    POINT,
    DATE,
    DECIMAL,
)

# Create some SQL types
int_type = INT()
string_type = STRING(length=100)
char_type = CHAR(length=10)
text_type = TEXT()
datetime_type = DATETIME()
timestamp_type = TIMESTAMP(timezone=True, precision=6)
bool_type = BOOLEAN()


class TestDataType(unittest.TestCase):
    ...
    # @parameterized.expand(
    #     [
    #         (int_type, "INT"),
    #         (string_type, "VARCHAR(100)"),
    #         (char_type, "CHAR(10)"),
    #         (text_type, "TEXT"),
    #         (datetime_type, "DATETIME(3)"),
    #         (timestamp_type, "TIMESTAMP(6)"),
    #         (bool_type, "TINYINT(1)"),
    #     ]
    # )
    # def test_types_mysql(self, type_: TypeEngine, result: str) -> None:
    #     self.assertEqual(type_.get_sql(DatabaseType.MYSQL), result)


type ColumnCustom[T] = Column[T]


class TableType(Table):
    __table_name__ = "table_type"

    pk: Column[INT] = Column(INT(), is_primary_key=True, is_auto_increment=False)
    strings: Column[VARCHAR] = Column(VARCHAR(255))
    integers: Column[INT] = Column(INT())
    floats: Column[FLOAT] = Column(FLOAT())
    points: Column[POINT] = Column(POINT())
    datetimes: Column[DATETIME] = Column(DATETIME())
    dates: Column[DATE] = Column(DATE())
    decimals: Column[DECIMAL] = Column(DECIMAL(precision=5, scale=2))


class TestTypes(unittest.TestCase):
    def test_create_table(self):
        TableType()


if __name__ == "__main__":
    unittest.main()
