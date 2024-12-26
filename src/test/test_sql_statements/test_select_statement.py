import unittest
import typing as tp
import sys
from pathlib import Path
from mysql.connector import MySQLConnection


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.common.interfaces import IRepositoryBase
from ormlambda.databases.my_sql import MySQLRepository
from config import config_dict  # noqa: E402
from ormlambda import Table, Column, BaseModel, ForeignKey  # noqa: E402


DDBBNAME = "__test_ddbb__"


class CSimple(Table):
    __table_name__ = "C"
    pk_c: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str]


class BSimple(Table):
    __table_name__ = "B"
    pk_b: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str]
    fk_c: Column[int]

    CSimple = ForeignKey[tp.Self, CSimple](CSimple, lambda self, c: self.fk_c == c.pk_c)


class AWithMultipleReferencesToB(Table):
    __table_name__ = "A"
    pk_a: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    data_a: Column[str]
    fk_b1: Column[int]
    fk_b2: Column[int]
    fk_b3: Column[int]

    B_fk_b1 = ForeignKey[tp.Self, BSimple](BSimple, lambda self, b: self.fk_b1 == b.pk_b)
    B_fk_b2 = ForeignKey[tp.Self, BSimple](BSimple, lambda self, b: self.fk_b2 == b.pk_b)
    B_fk_b3 = ForeignKey[tp.Self, BSimple](BSimple, lambda self, b: self.fk_b3 == b.pk_b)


class AModel(BaseModel[AWithMultipleReferencesToB]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, AWithMultipleReferencesToB, repository)


class CSimpleModel(BaseModel[CSimple]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, CSimple, repository)


class BSimpleModel(BaseModel[BSimple]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, BSimple, repository)


class TestJoinQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: IRepositoryBase[MySQLConnection] = MySQLRepository(**config_dict)
        cls.ddbb.database = DDBBNAME
        cls.ddbb.create_database(DDBBNAME, "replace")

        cls.model = AModel(cls.ddbb)
        CSimpleModel(cls.ddbb).create_table()
        BSimpleModel(cls.ddbb).create_table()
        cls.model.create_table()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_database(DDBBNAME)

    def test_new_select(self):
        self.model.select(AWithMultipleReferencesToB)
        real_query: str = "SELECT `A`.pk_a AS `A_pk_ a`, `A`.data_a AS `A_data_a`, `A`.fk_b1 AS `A_fk_b1`, `A`.fk_b2 AS `A_fk_b2`, `A`.fk_b3 AS `A_fk_b3` FROM A AS `A`"
        self.assertEqual(self.model.query, real_query)

    def test_new_select_context(self):
        select_a = self.model.select(
            lambda a: (
                a.data_a,
                a.B_fk_b1.name,
                a.B_fk_b2.name,
                a.B_fk_b3.name,
                a.B_fk_b1.CSimple.name,
                a.B_fk_b2.CSimple.name,
            ),
        )
        real_query: str = "SELECT A.data_a, b1.name as `b1.name`, b2.name as `b2.name`, b3.name as `b3.name` FROM A INNER JOIN B AS `b1` ON A.fk_b1 = b1.pk_b INNER JOIN B AS `b2` ON A.fk_b2 = b2.pk_b INNER JOIN B AS `b3` ON A.fk_b3 = b3.pk_b"
        self.model.query
        select_a
        self.assertEqual(self.model.query, real_query)


if __name__ == "__main__":
    unittest.main(failfast=True)
