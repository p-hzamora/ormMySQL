import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from ormlambda import Table, Column, BaseModel, ForeignKey  # noqa: E402
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

    def test_new_select(self):
        self.model.select(AWithMultipleReferencesToB)
        real_query: str = "SELECT `A`.pk_a AS `A_pk_a`, `A`.data_a AS `A_data_a`, `A`.fk_b1 AS `A_fk_b1`, `A`.fk_b2 AS `A_fk_b2`, `A`.fk_b3 AS `A_fk_b3` FROM A AS `A`"
        self.assertEqual(self.model.query, real_query)

    # # FIXME [ ]: Check why ForeignKey alias in 'a.B_fk_b1.CSimple' 'a.B_fk_b2.CSimple' it's not working as expected.
    # def test_new_select_context(self):
    #     res = self.model.select(
    #         lambda a: (
    #             a.data_a,
    #             self.model.alias(a.B_fk_b1.name, alias="b_b1_name"),
    #             self.model.alias(a.B_fk_b2.name, alias="b_b2_name"),
    #             self.model.alias(a.B_fk_b3.name, alias="b_b3_name"),
    #             # self.model.alias(a.B_fk_b1.CSimple.name, alias="b1_c_name"),
    #             # self.model.alias(a.B_fk_b2.CSimple.name, alias="b2_c_name"),
    #         ),
    #     )
    #     real_query: str = "SELECT `A`.data_a AS `A_data_a`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `B_fk_c_pk_c`.name AS `C_name`, `B_fk_c_pk_c`.name AS `C_name` FROM A AS `A` INNER JOIN B AS `A_fk_b1_pk_b` ON `A`.fk_b1 = `A_fk_b1_pk_b`.pk_b INNER JOIN B AS `A_fk_b2_pk_b` ON `A`.fk_b2 = `A_fk_b2_pk_b`.pk_b INNER JOIN B AS `A_fk_b3_pk_b` ON `A`.fk_b3 = `A_fk_b3_pk_b`.pk_b INNER JOIN C AS `B_fk_c_pk_c` ON `A_fk_b3_pk_b`.fk_c = `B_fk_c_pk_c`.pk_c"
    #     self.assertEqual(self.model.query(DIALECT),real_query)

    #     select = self.model.select(
    #         lambda x: (
    #             x.data_a,
    #             x.B_fk_b1.name,
    #         ),
    #         flavour=tuple,
    #     )
    #     print(select)


if __name__ == "__main__":
    unittest.main(failfast=True)
