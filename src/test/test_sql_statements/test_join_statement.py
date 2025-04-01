from __future__ import annotations
import unittest
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import BaseRepository, Table, Column, JoinType  # noqa: E402
from test.config import config_dict  # noqa: E402
from test.models import (  # noqa: E402
    TestTable,
)


DDBBNAME = "__test_ddbb__"
TABLETEST = TestTable.__table_name__


class JoinA(Table):
    __table_name__ = "a"
    pk_a: int = Column(int, is_primary_key=True, is_auto_increment=True)
    data_a: Column[str] = Column(str)


class JoinB(Table):
    __table_name__ = "b"
    pk_b: int = Column(int, is_primary_key=True, is_auto_increment=True)
    data_b: Column[str] = Column(str)
    fk_a: Column[int] = Column(int)
    fk_c: Column[int] = Column(int)


class JoinC(Table):
    __table_name__ = "c"
    pk_c: int = Column(int, is_primary_key=True, is_auto_increment=True)
    data_c: Column[str] = Column(str)
    fk_b: Column[int] = Column(int)


class TestJoinStatements(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: BaseRepository = MySQLRepository(**config_dict)

        cls.ddbb.create_database(DDBBNAME, "replace")
        cls.ddbb.database = DDBBNAME

        cls.model_a = ORM(JoinA, cls.ddbb)
        cls.model_b = ORM(JoinB, cls.ddbb)
        cls.model_c = ORM(JoinC, cls.ddbb)

        cls.model_a.create_table()
        cls.model_b.create_table()
        cls.model_c.create_table()

        a = [JoinA(x, f"data_a_pk{str(x)}") for x in range(1, 11)]
        c = [JoinC(x, f"data_a_pk{str(x)}") for x in range(1, 11)]
        b = [
            JoinB(1, fk_a=1, fk_c=2, data_b=None),
            JoinB(2, fk_a=1, fk_c=2, data_b="data_b_pk_2"),
            JoinB(3, fk_a=1, fk_c=2, data_b="data_b_pk_3"),
            JoinB(4, fk_a=1, fk_c=2, data_b="data_b_pk_4"),
            JoinB(5, fk_a=2, fk_c=2, data_b="data_b_pk_5"),
            JoinB(6, fk_a=2, fk_c=2, data_b="data_b_pk_6"),
            JoinB(7, fk_a=2, fk_c=2, data_b="data_b_pk_7"),
            JoinB(8, fk_a=2, fk_c=2, data_b="data_b_pk_8"),
            JoinB(9, fk_a=3, fk_c=2, data_b="data_b_pk_9"),
            JoinB(10, fk_a=3, fk_c=2, data_b="data_b_pk_10"),
        ]

        cls.model_a.insert(a)
        cls.model_b.insert(b)
        cls.model_c.insert(c)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ddbb.drop_database(DDBBNAME)

    # FIXME [x]: Review this method in the future
    def test_pass_multiple_joins(self):
        with self.model_b.join(
            [
                (JoinB.fk_a == JoinA.pk_a, JoinType.INNER_JOIN),
                (JoinB.fk_c == JoinC.pk_c, JoinType.INNER_JOIN),
            ]
        ):
            result1 = self.model_b.where([JoinB.fk_a == 2, JoinB.fk_c == 2]).select(
                (
                    JoinB.data_b,
                    JoinA.data_a,
                    JoinC.data_c,
                ),
                flavour=dict,
            )

        with self.model_b.join(
            (
                (JoinB.fk_a == JoinA.pk_a, JoinType.INNER_JOIN),
                (JoinB.fk_c == JoinC.pk_c, JoinType.INNER_JOIN),
            )
        ):
            result2 = self.model_b.where([JoinA.pk_a == 2, JoinC.pk_c == 2]).select(
                (
                    JoinB.data_b,
                    JoinA.data_a,
                    JoinC.data_c,
                ),
                flavour=dict,
            )

        self.assertTupleEqual(result1, result2)

    def test_pass_one_join(self):
        with self.model_b.join(
            [
                (JoinB.fk_a == JoinA.pk_a, JoinType.LEFT_EXCLUSIVE),
            ]
        ):
            select = self.model_b.where([JoinB.fk_a == 2]).select(
                (
                    JoinB.data_b,
                    JoinA.data_a,
                ),
                flavour=dict,
            )

        theorical_result = (
            {"b_data_b": "data_b_pk_5", "a_data_a": "data_a_pk2"},
            {"b_data_b": "data_b_pk_6", "a_data_a": "data_a_pk2"},
            {"b_data_b": "data_b_pk_7", "a_data_a": "data_a_pk2"},
            {"b_data_b": "data_b_pk_8", "a_data_a": "data_a_pk2"},
        )
        self.assertTupleEqual(select, theorical_result)

    # def test_used_of_count_agg_with_join_allowing_NULL(self):
    #     result = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.INNER_JOIN)
    #         .where(
    #             [
    #                 lambda b, a_foreign: a_foreign.pk_a == 1,
    #                 lambda b, _: b.fk_c == 2,
    #             ]
    #         )
    #         .select_one(
    #             lambda b, a: (self.model_a.count(lambda a: a.pk_a),),
    #             flavour=dict,
    #         )
    #     )
    #     self.assertEqual(result["count"], 4)

    # def test_used_of_pandas_as_flavour(self):
    #     import pandas as pd

    #     columns = [["ff", "aa", "count"]]
    #     result = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.INNER_JOIN)
    #         .group_by(lambda b, a: b.fk_a)
    #         .select(
    #             lambda b, a: (
    #                 b.fk_a,
    #                 a.data_a,
    #                 self.model_b.count(lambda b: b.fk_a),
    #             ),
    #             flavour=pd.DataFrame,
    #             columns=columns,
    #             cast_to_tuple=False,
    #         )
    #     )
    #     result_to_tuple = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.INNER_JOIN)
    #         .group_by(lambda b, a: b.fk_a)
    #         .select(
    #             lambda b, a: (
    #                 b.fk_a,
    #                 a.data_a,
    #                 self.model_b.count(lambda b: b.fk_a),
    #             ),
    #             flavour=tuple,
    #             cast_to_tuple=True,
    #         )
    #     )

    #     df2 = pd.DataFrame(columns=columns, data=result_to_tuple)
    #     self.assertTrue(result.equals(df2))

    # def test_alias(self):
    #     keys = self.model_b.select_one(
    #         lambda x: (
    #             self.model_b.alias(lambda x: x.data_b, "data_b_de b"),
    #             self.model_b.alias(lambda x: x.fk_a, "fk_a de b"),
    #         ),
    #         flavour=dict,
    #     )

    #     mssg: str = "SELECT b.data_b as `data_b_de b`, b.fk_a as `fk_a de b` FROM b\nLIMIT 1"

    #     self.assertTupleEqual(tuple(keys), ("data_b_de b", "fk_a de b"))
    #     self.assertEqual(mssg, self.model_b.query)


if __name__ == "__main__":
    unittest.main(failfast=True)
