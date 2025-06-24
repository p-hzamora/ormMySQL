import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from test.config import create_env_engine, create_engine_for_db, create_sakila_engine  # noqa: E402
from ormlambda import Table, Column, BaseModel, ForeignKey, ORM  # noqa: E402
from ormlambda.dialects import mysql
from test.models import Address, City, Country


DIALECT = mysql.dialect

DDBBNAME = "__test_ddbb__"


class D(Table):
    __table_name__ = "D"

    pk_d: Column[int] = Column(int, is_primary_key=True)
    name: Column[str]


class C(Table):
    __table_name__ = "C"
    pk_c: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    fk_d1: Column[int]
    fk_d2: Column[int]
    name: Column[str]

    D1 = ForeignKey["C", D](D, lambda self, d: self.fk_d1 == d.pk_d)
    D2 = ForeignKey["C", D](D, lambda self, d: self.fk_d2 == d.pk_d)


class B(Table):
    __table_name__ = "B"
    pk_b: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str]
    fk_c1: Column[int]
    fk_c2: Column[int]
    fk_c3: Column[int]

    C1 = ForeignKey["B", C](C, lambda self, c: self.fk_c1 == c.pk_c)
    C2 = ForeignKey["B", C](C, lambda self, c: self.fk_c2 == c.pk_c)
    C3 = ForeignKey["B", C](C, lambda self, c: self.fk_c3 == c.pk_c)


class A(Table):
    __table_name__ = "A"
    pk_a: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    data_a: Column[str]
    fk_b1: Column[int]
    fk_b2: Column[int]
    fk_b3: Column[int]

    B1 = ForeignKey["A", B](B, lambda self, b: self.fk_b1 == b.pk_b)
    B2 = ForeignKey["A", B](B, lambda self, b: self.fk_b2 == b.pk_b)
    B3 = ForeignKey["A", B](B, lambda self, b: self.fk_b3 == b.pk_b)


engine = create_env_engine()


class TestJoinQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        engine.create_schema(DDBBNAME, "replace")
        cls.db_engine = create_engine_for_db(DDBBNAME)

        cls.model = BaseModel(A, cls.db_engine)
        BaseModel(D, cls.db_engine).create_table()
        BaseModel(C, cls.db_engine).create_table()
        BaseModel(B, cls.db_engine).create_table()
        BaseModel(A, cls.db_engine).create_table()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db_engine.drop_schema(DDBBNAME)

    # def test_aa(self):
    #     engine = create_sakila_engine()
    #     res = ORM(Address, engine).where(lambda x: x.City.Country.country == 'Spain').select(
    #         lambda x: [
    #             x,
    #             x.City,
    #             x.City.Country,
    #         ]
    #     )

    #     res

    # FIXME [ ]: Check why ForeignKey alias in 'a.B_fk_b1.C' 'a.B_fk_b2.C' it's not working as expected.
    def test_new_select_context(self):
        res = self.model.select(
            lambda a: (
                a.data_a,
                # region All B1 possibilities
                a.B1.name,
                
                a.B3.C3.D1.name,
                a.B3.C3.D2.name,
                # endregion
            ),
        )
        real_query: str = "SELECT `A`.data_a AS `A_data_a`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `B_fk_c_pk_c`.name AS `C_name`, `B_fk_c_pk_c`.name AS `C_name` FROM A AS `A` INNER JOIN B AS `A_fk_b1_pk_b` ON `A`.fk_b1 = `A_fk_b1_pk_b`.pk_b INNER JOIN B AS `A_fk_b2_pk_b` ON `A`.fk_b2 = `A_fk_b2_pk_b`.pk_b INNER JOIN B AS `A_fk_b3_pk_b` ON `A`.fk_b3 = `A_fk_b3_pk_b`.pk_b INNER JOIN C AS `B_fk_c_pk_c` ON `A_fk_b3_pk_b`.fk_c = `B_fk_c_pk_c`.pk_c"
        self.assertEqual(res, real_query)

    # # FIXME [ ]: Check why ForeignKey alias in 'a.B_fk_b1.C' 'a.B_fk_b2.C' it's not working as expected.
    # def test_new_select_context(self):
    #     res = self.model.select(
    #         lambda a: (
    #             a.data_a,
    #             # region All B1 possibilities
    #             self.model.alias(a.B1.name, alias="a~B1~name"),
    #             self.model.alias(a.B1.C1.name, alias="a~B1~C1~name"),
    #             self.model.alias(a.B1.C2.name, alias="a~B1~C2~name"),
    #             self.model.alias(a.B1.C3.name, alias="a~B1~C3~name"),
    #             self.model.alias(a.B1.C1.D1.name, alias="a~B1~C1~D1~name"),
    #             self.model.alias(a.B1.C1.D2.name, alias="a~B1~C1~D2~name"),
    #             self.model.alias(a.B1.C2.D1.name, alias="a~B1~C2~D1~name"),
    #             self.model.alias(a.B1.C2.D2.name, alias="a~B1~C2~D2~name"),
    #             self.model.alias(a.B1.C3.D1.name, alias="a~B1~C3~D1~name"),
    #             self.model.alias(a.B1.C3.D2.name, alias="a~B1~C3~D2~name"),
    #             # endregion
    #             # region All B2 possibilities
    #             self.model.alias(a.B2.name, alias="a~B2~name"),
    #             self.model.alias(a.B2.C1.name, alias="a~B2~C1~name"),
    #             self.model.alias(a.B2.C2.name, alias="a~B2~C2~name"),
    #             self.model.alias(a.B2.C3.name, alias="a~B2~C3~name"),
    #             self.model.alias(a.B2.C1.D1.name, alias="a~B2~C1~D1~name"),
    #             self.model.alias(a.B2.C1.D2.name, alias="a~B2~C1~D2~name"),
    #             self.model.alias(a.B2.C2.D1.name, alias="a~B2~C2~D1~name"),
    #             self.model.alias(a.B2.C2.D2.name, alias="a~B2~C2~D2~name"),
    #             self.model.alias(a.B2.C3.D1.name, alias="a~B2~C3~D1~name"),
    #             self.model.alias(a.B2.C3.D2.name, alias="a~B2~C3~D2~name"),
    #             # endregion
    #             # region All B3 possibilities
    #             self.model.alias(a.B3.name, alias="a~B3~name"),
    #             self.model.alias(a.B3.C1.name, alias="a~B3~C1~name"),
    #             self.model.alias(a.B3.C2.name, alias="a~B3~C2~name"),
    #             self.model.alias(a.B3.C3.name, alias="a~B3~C3~name"),
    #             self.model.alias(a.B3.C1.D1.name, alias="a~B3~C1~D1~name"),
    #             self.model.alias(a.B3.C1.D2.name, alias="a~B3~C1~D2~name"),
    #             self.model.alias(a.B3.C2.D1.name, alias="a~B3~C2~D1~name"),
    #             self.model.alias(a.B3.C2.D2.name, alias="a~B3~C2~D2~name"),
    #             self.model.alias(a.B3.C3.D1.name, alias="a~B3~C3~D1~name"),
    #             self.model.alias(a.B3.C3.D2.name, alias="a~B3~C3~D2~name"),
    #             # endregion
    #         ),
    #     )
    #     real_query: str = "SELECT `A`.data_a AS `A_data_a`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `B_fk_c_pk_c`.name AS `C_name`, `B_fk_c_pk_c`.name AS `C_name` FROM A AS `A` INNER JOIN B AS `A_fk_b1_pk_b` ON `A`.fk_b1 = `A_fk_b1_pk_b`.pk_b INNER JOIN B AS `A_fk_b2_pk_b` ON `A`.fk_b2 = `A_fk_b2_pk_b`.pk_b INNER JOIN B AS `A_fk_b3_pk_b` ON `A`.fk_b3 = `A_fk_b3_pk_b`.pk_b INNER JOIN C AS `B_fk_c_pk_c` ON `A_fk_b3_pk_b`.fk_c = `B_fk_c_pk_c`.pk_c"
    #     self.assertEqual(res, real_query)

    # # FIXME [ ]: Check why ForeignKey alias in 'a.B_fk_b1.C' 'a.B_fk_b2.C' it's not working as expected.
    # def test_new_select_context(self):
    #     res = ORM(A, engine).select(lambda x: (x.B1.C1.D2.pk_d,))
    #     real_query: str = "SELECT `A`.data_a AS `A_data_a`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `A_fk_b3_pk_b`.name AS `B_name`, `B_fk_c_pk_c`.name AS `C_name`, `B_fk_c_pk_c`.name AS `C_name` FROM A AS `A` INNER JOIN B AS `A_fk_b1_pk_b` ON `A`.fk_b1 = `A_fk_b1_pk_b`.pk_b INNER JOIN B AS `A_fk_b2_pk_b` ON `A`.fk_b2 = `A_fk_b2_pk_b`.pk_b INNER JOIN B AS `A_fk_b3_pk_b` ON `A`.fk_b3 = `A_fk_b3_pk_b`.pk_b INNER JOIN C AS `B_fk_c_pk_c` ON `A_fk_b3_pk_b`.fk_c = `B_fk_c_pk_c`.pk_c"
    #     self.assertEqual(res, real_query)


if __name__ == "__main__":
    unittest.main(failfast=True)
