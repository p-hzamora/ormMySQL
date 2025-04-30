import sys
from pathlib import Path
import unittest
from parameterized import parameterized


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.models import Address, City, Country
from ormlambda.types.sql_type import SQLType
from ormlambda.types import DatabaseType
from ormlambda.types import (
    Integer,
    String,
    Text,
    Boolean,
    Timestamp,
    Char,
    DateTime,
)

from ormlambda.sql.schema_generator import SchemaGeneratorFactory


# Create some SQL types
int_type = Integer(autoincrement=True)
string_type = String(length=100)
char_type = Char(length=10)
text_type = Text(size="medium")
datetime_type = DateTime(precision=3)
timestamp_type = Timestamp(timezone=True, precision=6)
bool_type = Boolean()


class TestDataType(unittest.TestCase):
    @parameterized.expand(
        [
            (int_type, "INT AUTO_INCREMENT"),
            (string_type, "VARCHAR(100)"),
            (char_type, "CHAR(10)"),
            (text_type, "MEDIUMTEXT"),
            (datetime_type, "DATETIME(3)"),
            (timestamp_type, "TIMESTAMP(6)"),
            (bool_type, "TINYINT(1)"),
        ]
    )
    def test_types_mysql(self, type_: SQLType, result: str) -> None:
        self.assertEqual(type_.get_sql(DatabaseType.MYSQL), result)

    @parameterized.expand(
        [
            (int_type, "INTEGER"),
            (string_type, "VARCHAR(100)"),
            (char_type, "CHAR(10)"),
            (text_type, "TEXT"),
            (datetime_type, "DATETIME"),
            (timestamp_type, "TIMESTAMP"),
            (bool_type, "INTEGER"),
        ]
    )
    def test_types_sqlite(self, type_: SQLType, result: str) -> None:
        self.assertEqual(type_.get_sql(DatabaseType.SQLITE), result)


class TestSchemaGenerator(unittest.TestCase):
    def test_create_table(self):
        # co = SchemaGenerator(DatabaseType.MYSQL).create_table(Country)
        # ci = SchemaGenerator(DatabaseType.MYSQL).create_table(City)

        # FIXME [ ]: check who to deal with all types like bytes in sqlite. it's returning VARCHAR
        mysql_table = SchemaGeneratorFactory.get_generator(DatabaseType.MYSQL).create_table(Address)
        sqlite_table = SchemaGeneratorFactory.get_generator(DatabaseType.SQLITE).create_table(Address)
        EXPECTED_MYSQL_TABLE = "CREATE TABLE address (\n\taddress_id INT PRIMARY KEY,\n\taddress VARCHAR(255),\n\taddress2 VARCHAR(255),\n\tdistrict VARCHAR(255),\n\tcity_id INT,\n\tpostal_code VARCHAR(255),\n\tphone VARCHAR(255),\n\tlocation BLOB,\n\tlast_update DATETIME,\n\tFOREIGN KEY (city_id) REFERENCES city(city_id)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        EXPECTED_SQLITE_TABLE = "CREATE TABLE address (\n\taddress_id INTEGER PRIMARY KEY,\n\taddress TEXT,\n\taddress2 TEXT,\n\tdistrict TEXT,\n\tcity_id INTEGER,\n\tpostal_code TEXT,\n\tphone TEXT,\n\tlocation VARCHAR,\n\tlast_update DATETIME,\n\tFOREIGN KEY (city_id) REFERENCES city(city_id)\n);"

        self.assertEqual(mysql_table, EXPECTED_MYSQL_TABLE)
        self.assertEqual(sqlite_table, EXPECTED_SQLITE_TABLE)


if __name__ == "__main__":
    unittest.main()
