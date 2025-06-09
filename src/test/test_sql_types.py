import sys
from pathlib import Path
import unittest
from ormlambda.sql.type_api import TypeEngine
from parameterized import parameterized


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.sql.sqltypes import (
    INTEGER,
    STRING,
    CHAR,
    TEXT,
    DATETIME,
    TIMESTAMP,
    BOOLEAN,
)

# Create some SQL types
int_type = INTEGER()
string_type = STRING(length=100)
char_type = CHAR(length=10)
text_type = TEXT()
datetime_type = DATETIME()
timestamp_type = TIMESTAMP(timezone=True, precision=6)
bool_type = BOOLEAN()


class TestDataType(unittest.TestCase):
    @parameterized.expand(
        [
            (int_type, "INT"),
            (string_type, "VARCHAR(100)"),
            (char_type, "CHAR(10)"),
            (text_type, "TEXT"),
            (datetime_type, "DATETIME(3)"),
            (timestamp_type, "TIMESTAMP(6)"),
            (bool_type, "TINYINT(1)"),
        ]
    )
    def test_types_mysql(self, type_: TypeEngine, result: str) -> None:
        ...
        # self.assertEqual(type_.get_sql(DatabaseType.MYSQL), result)

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
    def test_types_sqlite(self, type_: TypeEngine, result: str) -> None:
        ...
        # self.assertEqual(type_.get_sql(DatabaseType.SQLITE), result)


class TestSchemaGenerator(unittest.TestCase):
    def test_create_table(self):
        ...
        # co = SchemaGenerator(DatabaseType.MYSQL).create_table(Country)
        # ci = SchemaGenerator(DatabaseType.MYSQL).create_table(City)

        # # FIXME [ ]: check who to deal with all types like bytes in sqlite. it's returning VARCHAR
        # mysql_table = SchemaGeneratorFactory.get_generator(DatabaseType.MYSQL).create_table(Address)
        # sqlite_table = SchemaGeneratorFactory.get_generator(DatabaseType.SQLITE).create_table(Address)
        # EXPECTED_MYSQL_TABLE = "CREATE TABLE address (\n\taddress_id INT PRIMARY KEY,\n\taddress VARCHAR(255),\n\taddress2 VARCHAR(255),\n\tdistrict VARCHAR(255),\n\tcity_id INT,\n\tpostal_code VARCHAR(255),\n\tphone VARCHAR(255),\n\tlocation BLOB,\n\tlast_update DATETIME,\n\tFOREIGN KEY (city_id) REFERENCES city(city_id)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        # EXPECTED_SQLITE_TABLE = "CREATE TABLE address (\n\taddress_id INTEGER PRIMARY KEY,\n\taddress TEXT,\n\taddress2 TEXT,\n\tdistrict TEXT,\n\tcity_id INTEGER,\n\tpostal_code TEXT,\n\tphone TEXT,\n\tlocation VARCHAR,\n\tlast_update DATETIME,\n\tFOREIGN KEY (city_id) REFERENCES city(city_id)\n);"

        # self.assertEqual(mysql_table, EXPECTED_MYSQL_TABLE)
        # self.assertEqual(sqlite_table, EXPECTED_SQLITE_TABLE)


if __name__ == "__main__":
    unittest.main()
