from __future__ import annotations
import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection, errors
import pandas as pd
from datetime import datetime

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import IRepositoryBase  # noqa: E402
from ormlambda import Table, Column, BaseModel  # noqa: E402
# from models import A, B, ModelAB  # noqa: F401

DDBBNAME = "__test_ddbb__"
TABLETEST = "__test_table__"
TABLETEST_AUTOGENERATED = "__test_table__AUTOGENERATED"


def create_instance_of_TestTable(number: int) -> list[TestTable]:
    if number <= 0:
        number = 1
    return [TestTable(*[x] * len(TestTable.__annotations__)) for x in range(1, number + 1)]


def create_instance_of_TestTableAUTOGENERATED(number: int) -> list[TestTable]:
    if number <= 0:
        number = 1
    return [TableWithAutoGenerated(*[x] * len(TableWithAutoGenerated.__annotations__)) for x in range(1, number + 1)]


class TestTable(Table):
    __table_name__ = TABLETEST
    Col1: int = Column[int](is_primary_key=True)
    Col2: int
    Col3: int
    Col4: int
    Col5: int
    Col6: int
    Col7: int
    Col8: int
    Col9: int
    Col10: int
    Col11: int
    Col12: int
    Col13: int
    Col14: int
    Col15: int
    Col16: int
    Col17: int
    Col18: int
    Col19: int
    Col20: int
    Col21: int
    Col22: int
    Col23: int
    Col24: int
    Col25: int


class TableWithAutoGenerated(Table):
    __table_name__ = TABLETEST_AUTOGENERATED

    Col_pk_auto_increment: int = Column[int](is_primary_key=True, is_auto_increment=True)
    Col_auto_generated: datetime = Column[datetime](is_auto_generated=True)
    Col3: int
    Col4: int


class TestTableModel(BaseModel[TestTable]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, TestTable, repository)


class TestTableAUTOModel(BaseModel[TableWithAutoGenerated]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, TableWithAutoGenerated, repository)


class TestSQLStatements(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)

        self.ddbb.create_database(DDBBNAME, "replace")
        self.ddbb.database = DDBBNAME
        self.tmodel = TestTableModel(self.ddbb)
        self.t_auto_model = TestTableAUTOModel(self.ddbb)

    def tearDown(self) -> None:
        self.ddbb.drop_database(DDBBNAME)

    def test_database_already_exists(self):
        with self.assertRaises(errors.DatabaseError):
            self.ddbb.create_database(DDBBNAME)

    def test_create_table(self):
        self.tmodel.create_table("replace")
        table_exists = self.ddbb.read_sql(f"SHOW TABLES LIKE '{TABLETEST}'")[0][0]

        self.assertEqual(
            table_exists,
            TABLETEST,
            msg=f"failed 'test_create_table' due to Table '{TABLETEST}' should exist after creation.",
        )

    def test_create_table_already_exists_fail(self):
        self.tmodel.create_table()
        with self.assertRaises(errors.ProgrammingError):
            self.tmodel.create_table()

    def test_insert(self):
        csv_data = pd.read_csv(Path(__file__).parent / "csv_table.csv").to_dict("records")
        self.tmodel.create_table()
        instance = [TestTable(**x) for x in csv_data]

        VERIFICATION = instance[15]
        self.tmodel.insert(instance)
        id = VERIFICATION.Col1

        select_query = self.tmodel.where(lambda x: x.Col1 == id, id=VERIFICATION.Col1).select_one()
        self.assertDictEqual(VERIFICATION.to_dict(), select_query.to_dict())

    # TODOM [x]: Add a test for update method once it has been created
    def test_update_with_properties_as_keys(self):
        self.tmodel.create_table()

        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.where(lambda x: x.Col1 == 3).update(
            {
                TestTable.Col2: 2,
                TestTable.Col5: 5,
                TestTable.Col13: 13,
            }
        )
        theorical_result = create_instance_of_TestTable(0)[0]
        theorical_result.Col2 = 2
        theorical_result.Col5 = 5
        theorical_result.Col13 = 13

        result = self.tmodel.where(lambda x: x.Col1 == 3).select_one()
        self.assertEqual(result, theorical_result)

    def test_update_with_str_as_keys(self):
        ROW_TO_UPDATE = 3
        self.tmodel.create_table()

        instance = create_instance_of_TestTable(3)
        self.tmodel.insert(instance)

        self.tmodel.where(lambda x: x.Col1 == ROW_TO_UPDATE, ROW_TO_UPDATE=ROW_TO_UPDATE).update(
            {
                "Col2": 22,
                "Col5": 55,
                "Col13": 133,
            },
        )

        result = self.tmodel.where(lambda x: x.Col1 == ROW_TO_UPDATE, ROW_TO_UPDATE=ROW_TO_UPDATE).select_one(
            lambda x: (
                x.Col2,
                x.Col5,
                x.Col13,
            ),
            flavour=tuple,
        )
        self.assertEqual(result, (22, 55, 133))

    def test_update_raising_KeyError(self):
        from models import Address

        self.tmodel.create_table()
        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        with self.assertRaises(KeyError):
            self.tmodel.where(lambda x: x.Col1 == 3).update(
                {
                    Address.address: 2,
                    TestTable.Col5: 5,
                    TestTable.Col13: 13,
                }
            )

    def test_upsert(self):
        self.tmodel.create_table()

        instance = create_instance_of_TestTable(0)[0]
        self.tmodel.insert(instance)

        instance.Col10 = 999
        self.tmodel.upsert(instance)

        select_row_0 = self.tmodel.where(lambda x: x.Col1 == 1).select_one()
        self.assertEqual(999, select_row_0.Col10)

    def test_limit(self):
        self.tmodel.create_table()
        instance = create_instance_of_TestTable(20)
        self.tmodel.insert(instance)

        limit = self.tmodel.limit(1).select()
        select_one = self.tmodel.select_one()
        self.assertEqual(limit[0], select_one)

    def test_offset(self):
        self.tmodel.create_table()
        instance = create_instance_of_TestTable(21)
        self.tmodel.insert(instance)

        offset = self.tmodel.offset(10).select_one()
        select_row_11 = self.tmodel.where(lambda x: x.Col1 == 11).select_one()
        self.assertEqual(offset, select_row_11)

    def test_delete(self):
        self.tmodel.create_table()
        instance = create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.where(lambda x: x.Col1 == 2).delete()
        select_all = self.tmodel.select(lambda x: x.Col1, flavour=tuple)
        self.assertTupleEqual((1, 3, 4, 5), select_all)

    # FIXME [ ]: Review this method in the future
    # def test_join(self):
    # #     modelA = ModelAB(A, self.ddbb)
    #     modelB = ModelAB(B, self.ddbb)

    #     insert_a = modelA.insert()
    #     insert_b = modelB.insert()

    #     join = modelA.join(A,B)
    #     self.assertEqual(join, None)

    def test_where(self):
        self.tmodel.create_table()
        instance = create_instance_of_TestTable(3)
        self.tmodel.insert(instance)
        where_clause = self.tmodel.where(lambda x: x.Col1 == 2).select_one()
        self.assertEqual(2, where_clause.Col13)

    def test_order(self):
        self.tmodel.create_table()
        instance = create_instance_of_TestTable(3)
        self.tmodel.insert(instance)

        query = self.tmodel.order(lambda x: x.Col10, order_type="DESC").select()
        self.assertListEqual([3, 2, 1], [x.Col10 for x in query])


class TestSQLStatementsWithAutoGenerated(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)
        self.ddbb.create_database(DDBBNAME, "replace")
        self.ddbb.database = DDBBNAME
        self.tmodel = TestTableAUTOModel(self.ddbb)
        self.tmodel.create_table()

    def tearDown(self) -> None:
        self.ddbb.drop_database(DDBBNAME)

    def create_test_table(self) -> None:
        return self.ddbb.execute(TableWithAutoGenerated.create_table_query())

    def create_instance_of_TestTable(self, number: int) -> list[TableWithAutoGenerated]:
        if number <= 0:
            raise ValueError

        return [TableWithAutoGenerated(*[x] * len(TableWithAutoGenerated.__annotations__)) for x in range(1, number + 1)]

    def test_insert_with_autogenerated_columms(self):
        instance = TableWithAutoGenerated(None, None, 3, 4)
        first_select = self.tmodel.select_one()
        self.tmodel.insert(instance)
        second_select = self.tmodel.select_one()

        self.assertTupleEqual(first_select, ())
        self.assertEqual(instance.Col_pk_auto_increment, None)
        self.assertEqual(instance.Col_auto_generated, None)

        self.assertIsNotNone(second_select.Col_pk_auto_increment)
        self.assertIsNotNone(second_select.Col_auto_generated)
        self.assertNotEqual((), second_select)

    def test_insert_with_autogenerated_columms_and_values_not_None(self):
        CURRENT_DATE = datetime(1998, 12, 16)
        CURRENT_PK = 10
        instance_10 = TableWithAutoGenerated(CURRENT_PK, CURRENT_DATE, 3, 4)
        first_select = self.tmodel.select_one()
        self.tmodel.insert(instance_10)
        second_select = self.tmodel.select_one()

        self.assertTupleEqual(first_select, ())

        self.assertEqual(second_select.Col_pk_auto_increment, CURRENT_PK)
        self.assertNotEqual(second_select.Col_auto_generated, CURRENT_DATE)

        instance_5 = TableWithAutoGenerated(5, CURRENT_DATE, 3, 4)
        self.tmodel.insert(instance_5)
        instance_5 = self.tmodel.where(lambda x: x.Col_pk_auto_increment == 5).select_one()
        self.assertEqual(instance_5.Col_pk_auto_increment, 5)
        self.assertNotEqual(instance_5.Col_auto_generated, CURRENT_DATE)

    def test_update_with_autogenerated_columms(self):
        CURRENT_DATETIME = datetime(1998, 12, 16)
        # region insert
        self.tmodel.insert(
            [
                TableWithAutoGenerated(Col3=13, Col4=14),
                TableWithAutoGenerated(Col3=23, Col4=24),
                TableWithAutoGenerated(Col3=33, Col4=34),
            ]
        )

        # endregion
        REAL_AUTOGENERATED_VALUE = self.tmodel.select_one(lambda x: x.Col_auto_generated, flavour=tuple)

        # region update
        self.tmodel.where(lambda x: x.Col_pk_auto_increment == 1).update(
            {
                TableWithAutoGenerated.Col_auto_generated: CURRENT_DATETIME,
                TableWithAutoGenerated.Col3: 333,
                TableWithAutoGenerated.Col4: 444,
            }
        )
        # endregion
        # check that the 'Col_auto_generated' col has not been updated with CURRENT_DATETIME and it is still keeping the 'REAL_AUTOGENERATED_VALUE'
        self.assertTupleEqual(
            self.tmodel.select(flavour=tuple),
            (
                (1, REAL_AUTOGENERATED_VALUE, 333, 444),
                (2, REAL_AUTOGENERATED_VALUE, 23, 24),
                (3, REAL_AUTOGENERATED_VALUE, 33, 34),
            ),
        )

        autogenerated_cols_tuple = self.tmodel.select(lambda x: x.Col_auto_generated, flavour=tuple)
        self.assertNotIn(CURRENT_DATETIME, autogenerated_cols_tuple)
        self.assertIn(REAL_AUTOGENERATED_VALUE, autogenerated_cols_tuple)

    def test_upsert_with_autogenerated_columns(self):
        def get_Col_auto_generated_value(number: int):
            return self.tmodel.where(lambda x: x.Col_pk_auto_increment == number, number=number).select_one().Col_auto_generated

        instance = create_instance_of_TestTableAUTOGENERATED(20)
        self.tmodel.insert(instance)

        CURRENT_DATETIME = datetime(1998, 12, 16)

        upsert_inst = (
            TableWithAutoGenerated(5, CURRENT_DATETIME, 9999, 10000),
            TableWithAutoGenerated(10, CURRENT_DATETIME, 9999, 10000),
            TableWithAutoGenerated(15, CURRENT_DATETIME, 9999, 10000),
            TableWithAutoGenerated(20, CURRENT_DATETIME, 9999, 10000),
        )

        self.tmodel.upsert(upsert_inst)
        select = self.tmodel.select(flavour=tuple)
        RESULT: tuple[tuple[int, ...]] = (
            (1, get_Col_auto_generated_value(1), 1, 1),
            (2, get_Col_auto_generated_value(2), 2, 2),
            (3, get_Col_auto_generated_value(3), 3, 3),
            (4, get_Col_auto_generated_value(4), 4, 4),
            (5, get_Col_auto_generated_value(5), 9999, 10000),
            (6, get_Col_auto_generated_value(6), 6, 6),
            (7, get_Col_auto_generated_value(7), 7, 7),
            (8, get_Col_auto_generated_value(8), 8, 8),
            (9, get_Col_auto_generated_value(9), 9, 9),
            (10, get_Col_auto_generated_value(10), 9999, 10000),
            (11, get_Col_auto_generated_value(11), 11, 11),
            (12, get_Col_auto_generated_value(12), 12, 12),
            (13, get_Col_auto_generated_value(13), 13, 13),
            (14, get_Col_auto_generated_value(14), 14, 14),
            (15, get_Col_auto_generated_value(15), 9999, 10000),
            (16, get_Col_auto_generated_value(16), 16, 16),
            (17, get_Col_auto_generated_value(17), 17, 17),
            (18, get_Col_auto_generated_value(18), 18, 18),
            (19, get_Col_auto_generated_value(19), 19, 19),
            (20, get_Col_auto_generated_value(20), 9999, 10000),
        )
        self.assertTupleEqual(RESULT, select)

    def test_select_with_flavour_as_tuple_when_query_is_empty(self):
        select = self.tmodel.select(lambda x: x.Col3, flavour=tuple)
        self.assertEqual(select, ())

    def test_select_one_with_flavour_as_tuple_when_query_is_empty(self):
        select = self.tmodel.select_one(lambda x: x.Col3, flavour=tuple)
        self.assertEqual(select, None)

    def test_select_with_flavour_as_list_when_query_is_empty(self):
        select = self.tmodel.select(lambda x: x.Col3, flavour=list)
        self.assertEqual(select, ())

    def test_select_one_with_flavour_as_list_when_query_is_empty(self):
        select = self.tmodel.select_one(lambda x: x.Col3, flavour=list)
        self.assertEqual(select, None)

    def test_select_with_flavour_as_set_when_query_is_empty(self):
        select = self.tmodel.select(lambda x: x.Col3, flavour=set)
        self.assertEqual(select, ())

    def test_select_one_with_flavour_as_set_when_query_is_empty(self):
        select = self.tmodel.select_one(lambda x: x.Col3, flavour=set)
        self.assertEqual(select, None)

    def test_select_with_flavour_as_dict_when_query_is_empty(self):
        select = self.tmodel.select(lambda x: x.Col3, flavour=dict)
        self.assertEqual(select, ())

    def test_select_one_with_flavour_as_dict_when_query_is_empty(self):
        select = self.tmodel.select_one(lambda x: x.Col3, flavour=dict)
        self.assertEqual(select, None)


if __name__ == "__main__":
    unittest.main(failfast=True)
