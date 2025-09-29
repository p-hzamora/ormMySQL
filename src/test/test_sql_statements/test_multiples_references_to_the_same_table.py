import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from pydantic import BaseModel
from test.config import create_env_engine, create_engine_for_db  # noqa: E402
from ormlambda import Table, Column, ORM, ForeignKey  # noqa: E402
from ormlambda.dialects import mysql
from ormlambda import Alias


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

        cls.model = ORM(A, cls.db_engine)
        ORM(D, cls.db_engine).create_table()
        ORM(C, cls.db_engine).create_table()
        ORM(B, cls.db_engine).create_table()
        ORM(A, cls.db_engine).create_table()

        cls.insert_data()

    @classmethod
    def insert_data(cls):
        # Insert data into table D (no dependencies)
        ORM(D, cls.db_engine).insert(
            [
                D(pk_d=1, name="Database Admin"),
                D(pk_d=2, name="System Manager"),
                D(pk_d=3, name="User Support"),
                D(pk_d=4, name="Technical Lead"),
                D(pk_d=5, name="Quality Assurance"),
                D(pk_d=6, name="Security Officer"),
                D(pk_d=7, name="Network Admin"),
                D(pk_d=8, name="Developer"),
                D(pk_d=9, name="Project Manager"),
                D(pk_d=10, name="Business Analyst"),
                D(pk_d=11, name="Data Scientist"),
                D(pk_d=12, name="UI Designer"),
                D(pk_d=13, name="DevOps Engineer"),
                D(pk_d=14, name="Product Owner"),
                D(pk_d=15, name="Consultant"),
            ]
        )

        # Insert data into table C (depends on D)
        ORM(C, cls.db_engine).insert(
            [
                C(fk_d1=1, fk_d2=2, name="Enterprise Solutions"),
                C(fk_d1=3, fk_d2=4, name="Customer Service"),
                C(fk_d1=5, fk_d2=6, name="Security Department"),
                C(fk_d1=7, fk_d2=8, name="Development Team"),
                C(fk_d1=9, fk_d2=10, name="Strategy Group"),
                C(fk_d1=11, fk_d2=12, name="Analytics Division"),
                C(fk_d1=13, fk_d2=14, name="Operations Unit"),
                C(fk_d1=15, fk_d2=1, name="Consulting Services"),
                C(fk_d1=2, fk_d2=3, name="Support Division"),
                C(fk_d1=4, fk_d2=5, name="Quality Control"),
                C(fk_d1=6, fk_d2=7, name="Infrastructure Team"),
                C(fk_d1=8, fk_d2=9, name="Product Development"),
                C(fk_d1=10, fk_d2=11, name="Research Group"),
                C(fk_d1=12, fk_d2=13, name="Design Operations"),
                C(fk_d1=14, fk_d2=15, name="Strategic Planning"),
            ]
        )

        # Insert data into table B (depends on C)
        ORM(B, cls.db_engine).insert(
            [
                B(name="North Region", fk_c1=1, fk_c2=2, fk_c3=3),
                B(name="South Region", fk_c1=4, fk_c2=5, fk_c3=6),
                B(name="East Region", fk_c1=7, fk_c2=8, fk_c3=9),
                B(name="West Region", fk_c1=10, fk_c2=11, fk_c3=12),
                B(name="Central Region", fk_c1=13, fk_c2=14, fk_c3=15),
                B(name="International Division", fk_c1=1, fk_c2=5, fk_c3=9),
                B(name="Domestic Operations", fk_c1=2, fk_c2=6, fk_c3=10),
                B(name="Digital Services", fk_c1=3, fk_c2=7, fk_c3=11),
                B(name="Traditional Services", fk_c1=4, fk_c2=8, fk_c3=12),
                B(name="Innovation Hub", fk_c1=1, fk_c2=8, fk_c3=15),
                B(name="Legacy Systems", fk_c1=2, fk_c2=9, fk_c3=13),
                B(name="Future Projects", fk_c1=3, fk_c2=10, fk_c3=14),
                B(name="Core Business", fk_c1=4, fk_c2=11, fk_c3=1),
                B(name="Expansion Unit", fk_c1=5, fk_c2=12, fk_c3=2),
                B(name="Optimization Team", fk_c1=6, fk_c2=13, fk_c3=3),
            ]
        )

        # Insert data into table A (depends on B)
        ORM(A, cls.db_engine).insert(
            [
                A(data_a="Project Alpha - Main Initiative", fk_b1=1, fk_b2=2, fk_b3=3),
                A(data_a="Project Beta - Secondary Focus", fk_b1=4, fk_b2=5, fk_b3=6),
                A(data_a="Project Gamma - Innovation Track", fk_b1=7, fk_b2=8, fk_b3=9),
                A(data_a="Project Delta - Optimization", fk_b1=10, fk_b2=11, fk_b3=12),
                A(data_a="Project Epsilon - Future Vision", fk_b1=13, fk_b2=14, fk_b3=15),
                A(data_a="Project Zeta - Cross-Regional", fk_b1=1, fk_b2=6, fk_b3=11),
                A(data_a="Project Eta - Digital Transform", fk_b1=2, fk_b2=7, fk_b3=12),
                A(data_a="Project Theta - Legacy Migration", fk_b1=3, fk_b2=8, fk_b3=13),
                A(data_a="Project Iota - Market Expansion", fk_b1=4, fk_b2=9, fk_b3=14),
                A(data_a="Project Kappa - Quality Enhancement", fk_b1=5, fk_b2=10, fk_b3=15),
                A(data_a="Project Lambda - Strategic Growth", fk_b1=1, fk_b2=9, fk_b3=14),
                A(data_a="Project Mu - Operational Excellence", fk_b1=2, fk_b2=10, fk_b3=1),
                A(data_a="Project Nu - Customer Focus", fk_b1=3, fk_b2=11, fk_b3=2),
                A(data_a="Project Xi - Technology Advancement", fk_b1=4, fk_b2=12, fk_b3=3),
                A(data_a="Project Omicron - Sustainability", fk_b1=5, fk_b2=13, fk_b3=4),
            ]
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db_engine.drop_schema(DDBBNAME)

    # FIXME [x]: Check why ForeignKey alias in 'a.B_fk_b1.C' 'a.B_fk_b2.C' it's not working as expected.
    def test_new_select_context_using_pydantic(self):
        class Response(BaseModel):
            name: str
            name_C1_D2: str
            name_C2_D2: str
            name_C3_D2: str

        res = self.model.where(lambda x: x.B3.C1.D2.name == "Developer").first(
            lambda a: (
                Alias(a.B3.C1.D2.name, "name"),
                Alias(a.B3.C1.D2.name, "name_C1_D2"),
                Alias(a.B3.C2.D2.name, "name_C2_D2"),
                Alias(a.B3.C3.D2.name, "name_C3_D2"),
                # endregion
            ),
            flavour=Response,
        )
        EXPECTED_RESPONSE = Response(
            name="Developer",
            name_C1_D2="Developer",
            name_C2_D2="Business Analyst",
            name_C3_D2="UI Designer",
        )
        self.assertEqual(res, EXPECTED_RESPONSE)

    # FIXME [x]: Check why ForeignKey alias in 'a.B_fk_b1.C' 'a.B_fk_b2.C' it's not working as expected.

    def test_new_select_context(self):
        VARIABLE = 3
        res = self.model.where(lambda x: x.pk_a == VARIABLE).first(
            lambda a: (
                # region All B1 possibilities
                Alias(a.pk_a, alias="PK"),
                Alias(a.B1.name, alias="a~B1~name"),
                Alias(a.B1.C1.name, alias="a~B1~C1~name"),
                Alias(a.B1.C2.name, alias="a~B1~C2~name"),
                Alias(a.B1.C3.name, alias="a~B1~C3~name"),
                Alias(a.B1.C1.D1.name, alias="a~B1~C1~D1~name"),
                Alias(a.B1.C1.D2.name, alias="a~B1~C1~D2~name"),
                Alias(a.B1.C2.D1.name, alias="a~B1~C2~D1~name"),
                Alias(a.B1.C2.D2.name, alias="a~B1~C2~D2~name"),
                Alias(a.B1.C3.D1.name, alias="a~B1~C3~D1~name"),
                Alias(a.B1.C3.D2.name, alias="a~B1~C3~D2~name"),
                # endregion
                # region All B2 possibilities
                Alias(a.B2.name, alias="a~B2~name"),
                Alias(a.B2.C1.name, alias="a~B2~C1~name"),
                Alias(a.B2.C2.name, alias="a~B2~C2~name"),
                Alias(a.B2.C3.name, alias="a~B2~C3~name"),
                Alias(a.B2.C1.D1.name, alias="a~B2~C1~D1~name"),
                Alias(a.B2.C1.D2.name, alias="a~B2~C1~D2~name"),
                Alias(a.B2.C2.D1.name, alias="a~B2~C2~D1~name"),
                Alias(a.B2.C2.D2.name, alias="a~B2~C2~D2~name"),
                Alias(a.B2.C3.D1.name, alias="a~B2~C3~D1~name"),
                Alias(a.B2.C3.D2.name, alias="a~B2~C3~D2~name"),
                # endregion
                # region All B3 possibilities
                Alias(a.B3.name, alias="a~B3~name"),
                Alias(a.B3.C1.name, alias="a~B3~C1~name"),
                Alias(a.B3.C2.name, alias="a~B3~C2~name"),
                Alias(a.B3.C3.name, alias="a~B3~C3~name"),
                Alias(a.B3.C1.D1.name, alias="a~B3~C1~D1~name"),
                Alias(a.B3.C1.D2.name, alias="a~B3~C1~D2~name"),
                Alias(a.B3.C2.D1.name, alias="a~B3~C2~D1~name"),
                Alias(a.B3.C2.D2.name, alias="a~B3~C2~D2~name"),
                Alias(a.B3.C3.D1.name, alias="a~B3~C3~D1~name"),
                Alias(a.B3.C3.D2.name, alias="a~B3~C3~D2~name"),
                # endregion
            ),
            flavour=dict,
        )
        EXPECTED = {
            "PK": 3,
            "a~B1~name": "Domestic Operations",
            "a~B1~C1~name": "Customer Service",
            "a~B1~C2~name": "Analytics Division",
            "a~B1~C3~name": "Quality Control",
            "a~B1~C1~D1~name": "User Support",
            "a~B1~C1~D2~name": "Technical Lead",
            "a~B1~C2~D1~name": "Data Scientist",
            "a~B1~C2~D2~name": "UI Designer",
            "a~B1~C3~D1~name": "Technical Lead",
            "a~B1~C3~D2~name": "Quality Assurance",
            "a~B2~name": "Digital Services",
            "a~B2~C1~name": "Security Department",
            "a~B2~C2~name": "Operations Unit",
            "a~B2~C3~name": "Infrastructure Team",
            "a~B2~C1~D1~name": "Quality Assurance",
            "a~B2~C1~D2~name": "Security Officer",
            "a~B2~C2~D1~name": "DevOps Engineer",
            "a~B2~C2~D2~name": "Product Owner",
            "a~B2~C3~D1~name": "Security Officer",
            "a~B2~C3~D2~name": "Network Admin",
            "a~B3~name": "Traditional Services",
            "a~B3~C1~name": "Development Team",
            "a~B3~C2~name": "Consulting Services",
            "a~B3~C3~name": "Product Development",
            "a~B3~C1~D1~name": "Network Admin",
            "a~B3~C1~D2~name": "Developer",
            "a~B3~C2~D1~name": "Consultant",
            "a~B3~C2~D2~name": "Database Admin",
            "a~B3~C3~D1~name": "Developer",
            "a~B3~C3~D2~name": "Project Manager",
        }
        self.assertEqual(res, EXPECTED)

    def test_select_a_lot_of_columns_with_a_lot_of_combines(self):
        VARIABLE = 3
        res = self.model.where(lambda x: x.pk_a == VARIABLE).first(
            lambda a: (
                a.pk_a,
                # region All B1 possibilities
                a.B1.name,
                a.B1.C1.name,
                a.B1.C2.name,
                a.B1.C3.name,
                a.B1.C1.D1.name,
                a.B1.C1.D2.name,
                a.B1.C2.D1.name,
                a.B1.C2.D2.name,
                a.B1.C3.D1.name,
                a.B1.C3.D2.name,
                # endregion
                # region All B2 possibilities
                a.B2.name,
                a.B2.C1.name,
                a.B2.C2.name,
                a.B2.C3.name,
                a.B2.C1.D1.name,
                a.B2.C1.D2.name,
                a.B2.C2.D1.name,
                a.B2.C2.D2.name,
                a.B2.C3.D1.name,
                a.B2.C3.D2.name,
                # endregion
                # region All B3 possibilities
                a.B3.name,
                a.B3.C1.name,
                a.B3.C2.name,
                a.B3.C3.name,
                a.B3.C1.D1.name,
                a.B3.C1.D2.name,
                a.B3.C2.D1.name,
                a.B3.C2.D2.name,
                a.B3.C3.D1.name,
                a.B3.C3.D2.name,
                # endregion
            ),
            flavour=dict,
        )
        EXPECTED = {
            "A_pk_a": 3,
            "A_B1_name": "Domestic Operations",
            "A_B1_C1_name": "Customer Service",
            "A_B1_C2_name": "Analytics Division",
            "A_B1_C3_name": "Quality Control",
            "A_B1_C1_D1_name": "User Support",
            "A_B1_C1_D2_name": "Technical Lead",
            "A_B1_C2_D1_name": "Data Scientist",
            "A_B1_C2_D2_name": "UI Designer",
            "A_B1_C3_D1_name": "Technical Lead",
            "A_B1_C3_D2_name": "Quality Assurance",
            "A_B2_name": "Digital Services",
            "A_B2_C1_name": "Security Department",
            "A_B2_C2_name": "Operations Unit",
            "A_B2_C3_name": "Infrastructure Team",
            "A_B2_C1_D1_name": "Quality Assurance",
            "A_B2_C1_D2_name": "Security Officer",
            "A_B2_C2_D1_name": "DevOps Engineer",
            "A_B2_C2_D2_name": "Product Owner",
            "A_B2_C3_D1_name": "Security Officer",
            "A_B2_C3_D2_name": "Network Admin",
            "A_B3_name": "Traditional Services",
            "A_B3_C1_name": "Development Team",
            "A_B3_C2_name": "Consulting Services",
            "A_B3_C3_name": "Product Development",
            "A_B3_C1_D1_name": "Network Admin",
            "A_B3_C1_D2_name": "Developer",
            "A_B3_C2_D1_name": "Consultant",
            "A_B3_C2_D2_name": "Database Admin",
            "A_B3_C3_D1_name": "Developer",
            "A_B3_C3_D2_name": "Project Manager",
        }
        self.assertDictEqual(res, EXPECTED)


if __name__ == "__main__":
    unittest.main(failfast=True)
