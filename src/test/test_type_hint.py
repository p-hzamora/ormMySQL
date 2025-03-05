import sys
from pathlib import Path
from typing import Optional
import unittest
from config import config_dict

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from models.address import AddressModel  # noqa: E402
from models import Address, City, Country  # noqa: E402


class TestTypeHint(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb = MySQLRepository(**config_dict)
        self.a_model = AddressModel(self.ddbb)

    def test_SELECT_method_passing_3_columns(self):
        response = self.a_model.select(lambda a: (a, a.City, a.City.Country))
        a, city, country = response
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(a[0], Address)
        self.assertIsInstance(city[0], City)
        self.assertIsInstance(country[0], Country)

    def test_SELECT_method_passing_1_column(self):
        response = self.a_model.select(lambda a: (a.City,))
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0][0], City)

    def test_SELECT_ONE_method_passing_0_column(self):
        response = self.a_model.select_one()
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_tuple_with_table_itself(self):
        response = self.a_model.select_one(lambda x: (x,))
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_the_same_table_itself(self):
        response = self.a_model.select_one(lambda x: x)
        self.assertIsInstance(response, Address)

    def test_SELECT_ONE_method_passing_3_columns_of_the_same_table(self):
        response = self.a_model.select_one(lambda x: (x.address, x.address2, x.city_id), flavour=tuple)
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0], str)
        self.assertIsInstance(response[1], Optional[str])
        self.assertIsInstance(response[2], int)

    def test_SELECT_ONE_method_passing_3_columns(self):
        response = self.a_model.select_one(
            lambda a: (
                a,
                a.City,
                a.City.Country,
            )
        )
        a, city, country = response
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(a, Address)
        self.assertIsInstance(city, City)
        self.assertIsInstance(country, Country)

    def test_SELECT_ONE_method_passing_1_column(self):
        response = self.a_model.select_one(lambda a: (a,))

        self.assertIsInstance(response, Address)
        self.assertIsInstance(response.address, str)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_DICT(self):
        response = self.a_model.select_one(lambda a: (a,), flavour=dict)
        self.assertIsInstance(response, dict)
        self.assertIsInstance(list(response.values())[0], int)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_TUPLE(self):
        response = self.a_model.select_one(lambda a: (a,), flavour=tuple)
        self.assertIsInstance(response, tuple)
        self.assertIsInstance(response[0], int)

    def test_SELECT_ONE_method_passing_1_column_and_flavour_attr_LIST(self):
        response = self.a_model.select_one(lambda a: (a,), flavour=list)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0], int)

    def test_SELECT_ONE_method_with_SET_as_flavour_newer_module(self):
        # COMMENT: if we used 'mysql-connector', the BLOB data will be returned as a 'bytearray' (an unhashable data type). However, if you use the newer 'mysql-connector-python' you'll retrieve 'bytes' which are hashable
        selection = self.a_model.select_one(lambda a: (a,), flavour=set)
        self.assertTrue(len(selection), 8)

    # def test_SELECT_ONE_method_with_SET_as_flavour_and_raises_TypeError(self):
    #     class TableWithBytearray(Table):
    #         __table_name__ = "bytearray_table"
    #         pk: int = Column(int, is_primary_key=True)
    #         bytearray_data: bytearray

    #     class BytearrayModel(BaseModel[TableWithBytearray]):
    #         def __new__[TRepo](cls, repository: IRepositoryBase) -> IStatements_two_generic[TableWithBytearray, TRepo]:
    #             return super().__new__(cls, TableWithBytearray, repository)

    #     DDBB_NAME: str = "__TEST_DATABASE__"
    #     self.ddbb.create_database(DDBB_NAME, "replace")
    #     new_db_config = config_dict.copy()

    #     new_db_config["database"] = DDBB_NAME
    #     db = MySQLRepository(**new_db_config)
    #     byte_model = BytearrayModel(db)
    #     byte_model.create_table()

    #     with self.assertRaises(TypeError):
    #         try:
    #             # COMMENT: if we used 'mysql-connector', the BLOB data will be returned as a 'bytearray' (an unhashable data type). However, if you use the newer 'mysql-connector-python' you'll retrieve 'bytes' which are hashable
    #             byte_model.insert(TableWithBytearray(1, bytearray(b"bytearray data")))
    #             byte_model.select(flavour=set)
    #         except TypeError as e:
    #             self.assertEqual(e.args[0], "unhashable type '<class 'bytearray'>' found in '<class 'tuple'>' when attempting to cast the result into a 'set' object")
    #             raise TypeError
    #         finally:
    #             db.drop_database(DDBB_NAME)


if __name__ == "__main__":
    unittest.main()
