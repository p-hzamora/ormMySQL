import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection, errors
import pandas as pd

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from test.config import config_dict  # noqa: E402
from orm.databases.my_sql import MySQLRepository  # noqa: E402
from orm.common.interfaces import IRepositoryBase  # noqa: E402
from orm import Table, Column, BaseModel, ForeignKey  # noqa: E402


DDBBNAME = "__test_ddbb__"
TABLETEST = "__test_table__"


class TestTable(Table):
    __table_name__ = TABLETEST
    Col1: int = Column(is_primary_key=True)
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


class TestTableModel(BaseModel[TestTable]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, TestTable, repository)


class B(Table):
    __table_name__ = "b"
    pk_b: int = Column[int](is_primary_key=True)


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column[int](is_primary_key=True)
    B = ForeignKey["A", B](__table_name__, B, lambda a, b: a.pk_a == b.pk_b)


class ModelAB[T](BaseModel[T]):
    def __new__[TRepo](cls, model: T, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, model, repository)


class TestSQLStatements(unittest.TestCase):
    def setUp(self) -> None:
        self.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)

        self.ddbb.create_database(DDBBNAME, "fail")
        self.ddbb.set_config({"database": DDBBNAME})
        self.tmodel = TestTableModel(self.ddbb)

    def tearDown(self) -> None:
        self.ddbb.drop_database(DDBBNAME)

    def create_test_table(self) -> None:
        return self.ddbb.execute(TestTable.create_table_query())

    def create_instance_of_TestTable(self, number: int) -> list[TestTable]:
        if number <= 0:
            number = 1
        return [TestTable(*[x] * len(TestTable.__annotations__)) for x in range(1, number + 1)]

    def test_database_already_exists(self):
        with self.assertRaises(errors.DatabaseError):
            self.ddbb.create_database(DDBBNAME)

    def test_create_table(self):
        self.create_test_table()
        self.ddbb.connect()
        cursor = self.ddbb.connection.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{TABLETEST}'")
        table_exists = cursor.fetchone()
        cursor.close()
        self.assertTupleEqual(table_exists, (TABLETEST,), msg=f"Table '{TABLETEST}' should exist after creation.")

    def test_create_table_already_exists_fail(self):
        self.create_test_table()
        with self.assertRaises(errors.ProgrammingError):
            self.create_test_table()

    def test_insert(self):
        csv_data = pd.read_csv(Path(__file__).parent / "csv_table.csv").to_dict("records")
        self.create_test_table()
        instance = [TestTable(**x) for x in csv_data]

        VERIFICATION = instance[15]
        self.tmodel.insert(instance)
        id = VERIFICATION.Col1

        select_query = self.tmodel.where(lambda x: x.Col1 == id, id=VERIFICATION.Col1).select_one()
        self.assertDictEqual(VERIFICATION.to_dict(), select_query.to_dict())

    # TODOM: Add a test for update method once it has been created
    def test_upsert(self):
        self.create_test_table()

        instance = self.create_instance_of_TestTable(0)[0]
        self.tmodel.insert(instance)

        instance.Col10 = 999
        self.tmodel.upsert(instance)

        select_row_0 = self.tmodel.where(lambda x: x.Col1 == 1).select_one()
        self.assertEqual(999, select_row_0.Col10)

    def test_limit(self):
        self.create_test_table()
        instance = self.create_instance_of_TestTable(20)
        self.tmodel.insert(instance)

        limit = self.tmodel.limit(1).select()
        select_one = self.tmodel.select_one()
        self.assertEqual(limit[0], select_one)

    def test_offset(self):
        self.create_test_table()
        instance = self.create_instance_of_TestTable(21)
        self.tmodel.insert(instance)

        offset = self.tmodel.offset(10).select_one()
        select_row_11 = self.tmodel.where(lambda x: x.Col1 == 11).select_one()
        self.assertEqual(offset, select_row_11)

    def test_delete(self):
        self.create_test_table()
        instance = self.create_instance_of_TestTable(5)
        self.tmodel.insert(instance)

        self.tmodel.where(lambda x: x.Col1 == 2).delete()
        select_all = self.tmodel.select(lambda x: (x.Col1,), flavour=tuple)
        select_all = tuple([x[0] for x in select_all])
        self.assertTupleEqual((1, 3, 4, 5), select_all)

    # FIXME [ ]: Review this method in the future
    # def test_join(self):
    #     modelA = ModelAB(A, self.ddbb)
    #     modelB = ModelAB(B, self.ddbb)

    #     insert_a = modelA.insert()
    #     insert_b = modelB.insert()

    #     join = modelA.join(A,B)
    #     self.assertEqual(join, None)

    def test_where(self):
        self.create_test_table()
        instance = self.create_instance_of_TestTable(3)
        self.tmodel.insert(instance)
        where_clause = self.tmodel.where(lambda x: x.Col1 == 2).select_one()
        self.assertEqual(2, where_clause.Col13)

    def test_order(self):
        self.create_test_table()
        instance = self.create_instance_of_TestTable(3)
        self.tmodel.insert(instance)

        query = self.tmodel.order(lambda x: x.Col10, order_type="DESC").select()
        self.assertListEqual([3, 2, 1], [x.Col10 for x in query])


if __name__ == "__main__":
    unittest.main()
