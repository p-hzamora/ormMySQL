# Standard libraries
# Third party libraries
import unittest
import sys
from pathlib import Path
from datetime import datetime
from mysql.connector import errors
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))



# Custom libraries
from orm import MySQLRepository  # noqa: E402


TDDBB_name = "__test_ddbb__"
TTABLE_name = "__test_table__"

data_config = {"user": "root", "password": "1234"}


class Test_my_sql(unittest.TestCase):

    def setUp(self) -> None:
        self.ddbb = MySQLRepository(**data_config).connect()
        self.ddbb.create_database(TDDBB_name,"replace")

    def tearDown(self) -> None:
        self.ddbb.drop_database(TDDBB_name)

    def test_database_already_exists(self):
        # Debe alcanzar un raise pero como esta contenido en el with, el programa no falla
        with self.assertRaises(errors.DatabaseError):
            self.ddbb.create_database(TDDBB_name)

    def test_create_insert_and_drop_table(self):
        class test_table(object):
            __slots__ = ("_factura", "_amount", "_fecha")

            def __init__(self, date: datetime, num_fac: str, amount: float = None) -> None:
                self._factura = num_fac
                self._amount = amount
                self._fecha = date

            @property
            def to_dict(self):
                return {var_name.removeprefix("_"): getattr(self, var_name) for var_name in self.__slots__}

        tbl_name = TTABLE_name

        TABLE = {}
        TABLE[tbl_name] = f"CREATE TABLE {tbl_name}(" "   id INT AUTO_INCREMENT PRIMARY KEY" "   ,factura CHAR(8) NOT NULL" "   ,amount DECIMAL(5,2)" "   ,fecha DATE NOT NULL" ")"

        values: list[test_table] = [
            test_table(datetime.now(), "23/00001", 499.99).to_dict,
            test_table(datetime.now(), "23/00002", 20.5).to_dict,
            test_table(datetime.now(), "23/00003", 800.00).to_dict,
        ]
        self.ddbb.create_table(TABLE[tbl_name])
        self.ddbb.insert(tbl_name, values)
        self.ddbb.drop_table(tbl_name)

    def test_insert_table_from_df(self):
        df = pd.read_csv(Path(__file__).parent / "csv_table.csv")
        self.ddbb.create_table(data=df, name=TTABLE_name)
        self.ddbb.drop_table(TTABLE_name)

    def test_create_table_already_exists_fail(self):
        df = pd.read_csv(Path(__file__).parent / "csv_table.csv")
        self.ddbb.create_table(data=df.head(), name=TTABLE_name)

        with self.assertRaises(errors.DatabaseError):
            self.ddbb.create_table(df, TTABLE_name)

    def test_create_table_already_exists_replace(self):
        df = pd.read_csv(Path(__file__).parent / "csv_table.csv")
        self.ddbb.create_table(data=df.head(), name=TTABLE_name)

        self.ddbb.create_table(df, TTABLE_name, "replace")

    def test_read_sql(self):
        df = pd.read_csv(Path(__file__).parent / "csv_table.csv")
        self.ddbb.create_table(data=df.head(), name=TTABLE_name)

        result_all = self.ddbb.read_sql(f"SELECT * FROM {TTABLE_name}",pd.DataFrame)
        result_col = self.ddbb.read_sql(f"SELECT Col2 FROM {TTABLE_name}",tuple)
        result_unic = self.ddbb.read_sql(f"SELECT Col2 FROM {TTABLE_name} WHERE Col1 = 62044",tuple)
        result_row_dicc = self.ddbb.read_sql(f"SELECT * FROM {TTABLE_name} WHERE Col1 = 6623", dict)
        result_row_tuple = self.ddbb.read_sql(f"SELECT * FROM {TTABLE_name} WHERE Col1 = 6623", tuple)

        my_tuple = (
            6623,
            94092,
            38900,
            92190,
            16993,
            39016,
            11457,
            32841,
            60624,
            29787,
            12890,
            45305,
            53506,
            30572,
            50837,
            86671,
            16190,
            17628,
            37027,
            11625,
            13731,
            99635,
            87378,
            49801,
            83170,
        )

        dicc = {
            "Col1": 6623,
            "Col2": 94092,
            "Col3": 38900,
            "Col4": 92190,
            "Col5": 16993,
            "Col6": 39016,
            "Col7": 11457,
            "Col8": 32841,
            "Col9": 60624,
            "Col10": 29787,
            "Col11": 12890,
            "Col12": 45305,
            "Col13": 53506,
            "Col14": 30572,
            "Col15": 50837,
            "Col16": 86671,
            "Col17": 16190,
            "Col18": 17628,
            "Col19": 37027,
            "Col20": 11625,
            "Col21": 13731,
            "Col22": 99635,
            "Col23": 87378,
            "Col24": 49801,
            "Col25": 83170,
        }

        self.assertIsInstance(result_all[0], pd.DataFrame)
        self.assertEqual([x[0] for x in result_col], [77642, 93631, 58778, 94092, 16228])
        self.assertEqual(result_unic[0][0], 93631)
        self.assertEqual(result_row_dicc[0], dicc)
        self.assertEqual(result_row_tuple[0], my_tuple)

    def test_upsert(self):
        values = [
            {"id_unique": 100, "col1": 1, "col2": 2, "col3": 3, "col4": 4, "col5": 5},
            {"id_unique": 200, "col1": 7, "col2": 8, "col3": 9, "col4": 10, "col5": 11},
            {
                "id_unique": 300,
                "col1": 13,
                "col2": 14,
                "col3": 15,
                "col4": 16,
                "col5": 17,
            },
        ]

        new_val_100 = {
            "id_unique": 100,
            "col1": 111,
            "col2": 222,
            "col3": 333,
            "col4": 444,
            "col5": 555,
        }

        query = (
            f"CREATE TABLE {TTABLE_name}("
            "   id INT AUTO_INCREMENT PRIMARY KEY,"
            "   id_unique INT, "
            "   col1 INT,"
            "   col2 INT,"
            "   col3 INT,"
            "   col4 INT,"
            "   col5 INT,"
            "   CONSTRAINT `unique_id` UNIQUE(id_unique)"
            "   )"
        )

        self.ddbb.create_table(data=query, name=TTABLE_name)

        cols = "id_unique, col1, col2, col3, col4, col5"

        # insert in empty table
        self.ddbb.upsert(TTABLE_name, values)
        prev_dicc = self.ddbb.read_sql(f"SELECT {cols} FROM {TTABLE_name} LIMIT 1",dict)
        self.assertDictEqual(prev_dicc[0], values[0])

        # update values currently in empty table
        self.ddbb.upsert(
            TTABLE_name,
            {
                "id_unique": 100,
                "col1": 111,
                "col2": 222,
                "col3": 333,
                "col4": 444,
                "col5": 555,
            },
        )
        current_dicc = self.ddbb.read_sql(f"SELECT {cols} FROM {TTABLE_name} WHERE id_unique = 100",dict)
        self.assertDictEqual(current_dicc[0], new_val_100)

        # insert news values
        self.ddbb.upsert(TTABLE_name, {"id_unique": 101})
        self.ddbb.upsert(
            TTABLE_name,
            {
                "id_unique": 101,
                "col1": 101,
                "col2": 101,
                "col3": 101,
                "col4": 101,
                "col5": 101,
            },
        )

if __name__ == "__main__":
    unittest.main()
