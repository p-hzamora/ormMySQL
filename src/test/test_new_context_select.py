import unittest
import typing as tp
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql.clauses.select import Select
from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import IRepositoryBase, Table, Column, BaseModel, JoinType, ForeignKey  # noqa: E402


DDBBNAME = "__test_ddbb__"


class BSimple(Table):
    __table_name__ = "B"
    pk_b: int = Column(is_primary_key=True, is_auto_increment=True)
    name: str
    fk_c: int


class CSimple(Table):
    __table_name__ = "C"
    pk_b: int = Column(is_primary_key=True, is_auto_increment=True)
    name: str


class AWithMultipleReferencesToB(Table):
    __table_name__ = "A"
    pk_a: int = Column(is_primary_key=True, is_auto_increment=True)
    data_a: str
    fk_b1: int
    fk_b2: int
    fk_b3: int

    B_fk_b1 = ForeignKey[tp.Self, BSimple](__table_name__, BSimple, lambda self, b: self.fk_b1 == b.pk_b)
    B_fk_b2 = ForeignKey[tp.Self, BSimple](__table_name__, BSimple, lambda self, b: self.fk_b2 == b.pk_b)
    B_fk_b3 = ForeignKey[tp.Self, BSimple](__table_name__, BSimple, lambda self, b: self.fk_b3 == b.pk_b)


class TestJoinQueries(unittest.TestCase):
    def test_new_select_context(self):
        select_a = Select[AWithMultipleReferencesToB](
            (AWithMultipleReferencesToB,),
            lambda a: (
                a.data_a,
                a.B_fk_b1.name,
                a.B_fk_b2.name,
                a.B_fk_b3.name,
            ),
        )
        real_query: str = "SELECT A.data_a, b1.name as `b1.name`, b2.name as `b2.name`, b3.name as `b3.name` FROM A INNER JOIN B AS `b1` ON A.fk_b1 = b1.pk_b INNER JOIN B AS `b2` ON A.fk_b2 = b2.pk_b INNER JOIN B AS `b3` ON A.fk_b3 = b3.pk_b"
        select_a.query
        self.assertEqual(select_a.query, real_query)


if __name__ == "__main__":
    unittest.main(failfast=True)
