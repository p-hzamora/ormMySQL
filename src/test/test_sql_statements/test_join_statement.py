from __future__ import annotations
from datetime import datetime
import unittest
import sys
from pathlib import Path
from mysql.connector import MySQLConnection

from ormlambda.sql.comparer import Comparer


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from config import config_dict  # noqa: E402
from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import BaseRepository, Table, Column, BaseModel, JoinType  # noqa: E402
from models import (  # noqa: E402
    TestTable,
    ModelAB,
    A,
    B,
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


class JoinAModel(BaseModel[JoinA]):
    def __new__[TRepo](cls, repository: BaseRepository):
        return super().__new__(cls, JoinA, repository)


class JoinBModel(BaseModel[JoinB]):
    def __new__[TRepo](cls, repository: BaseRepository):
        return super().__new__(cls, JoinB, repository)


class JoinCModel(BaseModel[JoinC]):
    def __new__[TRepo](cls, repository: BaseRepository):
        return super().__new__(cls, JoinC, repository)


class TestJoinStatements(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ddbb: BaseRepository = MySQLRepository(**config_dict)

        cls.ddbb.create_database(DDBBNAME, "replace")
        cls.ddbb.database = DDBBNAME

        cls.model_a = JoinAModel(cls.ddbb)
        cls.model_b = JoinBModel(cls.ddbb)
        cls.model_c = JoinCModel(cls.ddbb)

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
                ("JA", JoinB.fk_a == JoinA.pk_a, JoinType.INNER_JOIN),
                ("JC", JoinB.fk_c == JoinC.pk_c, JoinType.INNER_JOIN),
            ]
        ) as ctx:
            result1 = self.model_b.where([JoinB.fk_a == 2, JoinB.fk_c == 2]).select(
                (
                    JoinB.data_b,
                    ctx.JA.data_a,
                    ctx.JC.data_c,
                ),
                flavour=dict,
                columns=[1, 2, 3, 4],
            )

        with self.model_b.join(
            (
                ("JA", JoinB.fk_a == JoinA.pk_a, JoinType.INNER_JOIN),
                ("JC", JoinB.fk_c == JoinC.pk_c, JoinType.INNER_JOIN),
            )
        ) as ctx:
            result2 = self.model_b.where([ctx.JA.pk_a == 2, ctx.JC.pk_c == 2]).select((JoinB.data_b, ctx.JA.data_a, ctx.JC.data_c), flavour=dict)

        self.assertTupleEqual(result1, result2)

    # def test_pass_one_join(self):
    #     select = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.LEFT_EXCLUSIVE)
    #         .where(
    #             [
    #                 lambda b_var, _: b_var.fk_a == 2,
    #             ]
    #         )
    #         .select(lambda b, a: (b.data_b, a.data_a), flavour=dict)
    #     )

    #     theorical_result = (
    #         {"b_data_b": "data_b_pk_5", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_6", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_7", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_8", "a_data_a": "data_a_pk2"},
    #     )
    #     self.assertTupleEqual(select, theorical_result)

    # def test_pass_one_join_with_where(self):
    #     select = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.LEFT_EXCLUSIVE)
    #         .where(lambda b_var, _: b_var.fk_a == 2)
    #         .select(
    #             lambda b, a: (
    #                 b.data_b,
    #                 a.data_a,
    #             ),
    #             flavour=dict,
    #         )
    #     )

    #     theorical_result = (
    #         {"b_data_b": "data_b_pk_5", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_6", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_7", "a_data_a": "data_a_pk2"},
    #         {"b_data_b": "data_b_pk_8", "a_data_a": "data_a_pk2"},
    #     )
    #     self.assertTupleEqual(select, theorical_result)

    # def test_used_of_count_agg_with_join_deleting_NULL(self):
    #     result = (
    #         self.model_b.join(JoinA, lambda b, a: b.fk_a == a.pk_a, JoinType.LEFT_EXCLUSIVE)
    #         .where(
    #             [
    #                 lambda b, a_foreign: a_foreign.pk_a == 1,
    #                 lambda b, _: b.fk_c == 2,
    #                 lambda b, _: b.data_b is not None,
    #             ]
    #         )
    #         .select_one(
    #             lambda b, a: (self.model_a.count(lambda a: a.pk_a),),
    #             flavour=dict,
    #         )
    #     )
    #     self.assertEqual(result["count"], 3)

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

    def test_join(self):
        """
        New way to use join with 'with' clause
        """
        ddbb: BaseRepository = MySQLRepository(**config_dict)
        ddbb.create_database(DDBBNAME, "replace")
        ddbb.database = DDBBNAME

        modelA = ModelAB(A, ddbb)
        modelB = ModelAB(B, ddbb)

        a_insert = [A(x, "a", "data_a", datetime.today(), f"pk_with_value_{x}") for x in range(1, 6)]
        b_insert = [
            *[B(None, "data_b", 1, "pk_b_with_data_1") for x in range(20)],
            *[B(None, "data_b", 2, "pk_b_with_data_2") for x in range(10)],
            *[B(None, "data_b", 3, "pk_b_with_data_3") for x in range(5)],
            B(None, "data_b", 4, "pk_b_with_data_4"),
        ]

        modelA.create_table()
        modelB.create_table()
        modelA.insert(a_insert)
        modelB.insert(b_insert)

        with modelB.join(
            [
                ("A", B.fk_a == A.pk_a, JoinType.LEFT_EXCLUSIVE),
            ]
        ) as ctx:
            select = modelB.where(ctx.A.pk_a >= 3).select_one(modelB.count("*"), flavour=dict, by=JoinType.LEFT_EXCLUSIVE)
        self.assertEqual(select["count"], 6)
        ddbb.drop_database(DDBBNAME)


if __name__ == "__main__":
    comp = Comparer[JoinA, str, JoinB, str](JoinA.data_a == JoinB.data_b)
    comp.left_condition

    unittest.main(failfast=True)
