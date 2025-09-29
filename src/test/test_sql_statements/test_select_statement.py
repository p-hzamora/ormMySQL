import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from ormlambda import Table, Column, BaseModel, ForeignKey, Alias  # noqa: E402
from ormlambda.dialects import mysql

DIALECT = mysql.dialect

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

    CSimple = ForeignKey["BSimple", CSimple](CSimple, lambda self, c: self.fk_c == c.pk_c)


class AWithMultipleReferencesToB(Table):
    __table_name__ = "A"
    pk_a: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    data_a: Column[str]
    fk_b1: Column[int]
    fk_b2: Column[int]
    fk_b3: Column[int]

    B_fk_b1 = ForeignKey["AWithMultipleReferencesToB", BSimple](BSimple, lambda self, b: self.fk_b1 == b.pk_b)
    B_fk_b2 = ForeignKey["AWithMultipleReferencesToB", BSimple](BSimple, lambda self, b: self.fk_b2 == b.pk_b)
    B_fk_b3 = ForeignKey["AWithMultipleReferencesToB", BSimple](BSimple, lambda self, b: self.fk_b3 == b.pk_b)


engine = create_env_engine()


class TestJoinQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        engine.create_schema(DDBBNAME, "replace")
        cls.db_engine = create_engine_for_db(DDBBNAME)

        cls.model = BaseModel(AWithMultipleReferencesToB, cls.db_engine)
        BaseModel(CSimple, cls.db_engine).create_table()
        BaseModel(BSimple, cls.db_engine).create_table()
        cls.model.create_table()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db_engine.drop_schema(DDBBNAME)


if __name__ == "__main__":
    unittest.main(failfast=True)
