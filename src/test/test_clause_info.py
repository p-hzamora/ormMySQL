from __future__ import annotations
from datetime import datetime
import sys
from pathlib import Path
from types import NoneType
from typing import Any, TYPE_CHECKING, Type
import unittest
from parameterized import parameterized
from shapely import Point


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

if TYPE_CHECKING:
    from ormlambda.sql.clause_info import AggregateFunctionBase
    from ormlambda.dialects import Dialect
from ormlambda.common.errors import NotKeysInIAggregateError
from ormlambda.databases.my_sql.clauses.ST_AsText import ST_AsText
from ormlambda.databases.my_sql.clauses.ST_Contains import ST_Contains
from ormlambda.sql.clause_info import ClauseInfo, ClauseInfoContext

from ormlambda.sql import functions as func
from test.models import A, C, TableType
from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def ClauseInfoMySQL[T](*args, **kwargs) -> ClauseInfo[T]:
    return ClauseInfo(*args, **kwargs, dialect=DIALECT)


class TestClauseInfo(unittest.TestCase):
    def test_passing_only_table(self):
        ci = ClauseInfoMySQL(A)
        self.assertEqual(ci.query(DIALECT), "a")

    @parameterized.expand(
        (
            (A, "name", "name"),
            (None, "name", "'name'"),
        )
    )
    def test_column_property(self, table, column, result):
        ci = ClauseInfoMySQL(table, column, "alias_table", "alias_clause")
        self.assertEqual(ci.column, result)

    def test_passing_only_table_with_alias_table(self):
        ci = ClauseInfoMySQL(A, alias_table=lambda x: "custom_table_name")
        self.assertEqual(ci.query(DIALECT), "a AS `custom_table_name`")

    def test_passing_only_table_with_alias_table_placeholder_of_column(self):
        with self.assertRaises(ValueError) as err:
            try:
                ClauseInfoMySQL(A, alias_table=lambda x: "{column}").query(DIALECT)
            except ValueError as err:
                mssg = "You cannot use {column} placeholder without using 'column' attribute"
                self.assertEqual(str(err), mssg)
                raise ValueError

    def test_passing_only_column_with_alias_table_placeholder_of_table(self):
        with self.assertRaises(ValueError) as err:
            try:
                ClauseInfoMySQL(None, "random_value", alias_clause=lambda x: "{table}").query(DIALECT)
            except ValueError as err:
                mssg = "You cannot use {table} placeholder without using 'table' attribute"
                self.assertEqual(str(err), mssg)
                raise ValueError

    def test_passing_only_table_with_alias_table_placeholder_of_table(self):
        ci = ClauseInfoMySQL(A, alias_table=lambda x: "{table}")
        self.assertEqual(ci.query(DIALECT), "a AS `a`")

    def test_constructor(self):
        ci = ClauseInfoMySQL(A, A.pk_a)
        self.assertEqual(ci.query(DIALECT), "a.pk_a")

    def test_passing_callable_alias_clause(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_clause=lambda x: "resolver_with_lambda_{column}")
        self.assertEqual(ci.query(DIALECT), "a.name_a AS `resolver_with_lambda_name_a`")

    def test_passing_string_with_placeholder_alias_clause(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_clause="resolver_with_lambda_{column}")
        self.assertEqual(ci.query(DIALECT), "a.name_a AS `resolver_with_lambda_name_a`")

    def test_passing_callable_alias_clause_with_placeholder(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_clause=lambda x: "resolver_with_lambda_{table}")
        self.assertEqual(ci.query(DIALECT), "a.name_a AS `resolver_with_lambda_a`")

    @parameterized.expand(
        (
            (A.pk_a, "pk_a", int),
            (A.name_a, "name_a", str),
            (A.data_a, "data_a", str),
            (A.date_a, "date_a", datetime),
            (A.value, "value", str),
        )
    )
    def test_passing_callable_and_custom_method(self, column, string_col: str, result: object):
        def message_placeholder(ci: ClauseInfo):
            return ci.dtype.__name__

        ci = ClauseInfoMySQL(A, column, alias_clause=message_placeholder)
        self.assertEqual(ci.query(DIALECT), f"a.{string_col} AS `{result.__name__}`")

    @parameterized.expand(
        (
            (A.pk_a, "pk_a", "INTEGER"),
            (A.name_a, "name_a", "TEXT"),
            (A.data_a, "data_a", "TEXT"),
            (A.date_a, "date_a", 'DATETIME'),
            (A.value, "value", "TEXT"),
        )
    )
    def test_custom_message_placeholder(self, column, string_col: str, result: object):
        def message_placeholder(ci: ClauseInfo):
            return f"{type(ci.dbtype).__visit_name__}~" +"{column}"

        ci = ClauseInfoMySQL(A, column, alias_clause=message_placeholder)
        self.assertEqual(ci.query(DIALECT), f"a.{string_col} AS `{result}~{string_col}`")

    def test_passing_callable_alias_table(self):
        ci = ClauseInfoMySQL(A, A.date_a, alias_table=lambda x: "custom_alias_for_{table}_table")
        self.assertEqual(ci.query(DIALECT), "`custom_alias_for_a_table`.date_a")

    def test_passing_placeholder_as_alias(self):
        ci = ClauseInfoMySQL(A, A.date_a, alias_table="{table}")
        self.assertEqual(ci.query(DIALECT), "`a`.date_a")

    def test_call_A_withou_alias(self):
        ci = ClauseInfoMySQL(A, A.date_a)
        self.assertEqual(ci.query(DIALECT), "a.date_a")

    def test_passing_callable_alias_table_with_placeholder(self):
        ci = ClauseInfoMySQL(A, A.date_a, alias_table=lambda x: "custom_alias_for_{column}_column")
        self.assertEqual(ci.query(DIALECT), "`custom_alias_for_date_a_column`.date_a")

    def test_passing_asterisk(self):
        ci = ClauseInfoMySQL(A, "*")
        self.assertEqual(ci.query(DIALECT), "a.pk_a, a.name_a, a.data_a, a.date_a, a.value")

    def test_hardcoding_asterisk(self):
        ci = ClauseInfoMySQL(A, "*", keep_asterisk=True)
        self.assertEqual(ci.query(DIALECT), "a.*")

    def test_hardcoding_asterisk_with_alias_table(self):
        ci = ClauseInfoMySQL(A, "*", alias_table="new_name", keep_asterisk=True)
        self.assertEqual(ci.query(DIALECT), "`new_name`.*")

    def test_passing_table(self):
        ci = ClauseInfoMySQL(A, A)
        self.assertEqual(ci.query(DIALECT), "a.pk_a, a.name_a, a.data_a, a.date_a, a.value")

    def test_passing_alias_table(self):
        ci = ClauseInfoMySQL(A, A.data_a, "ALIAS_TABLE")
        self.assertEqual(ci.query(DIALECT), "`ALIAS_TABLE`.data_a")

    def test_passing_alias_clause(self):
        ci = ClauseInfoMySQL(A, A.data_a, None, "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query(DIALECT), "a.data_a AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_with_alias_table_and_alias_clause(self):
        ci = ClauseInfoMySQL(A, A.pk_a, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query(DIALECT), "`ALIAS_TABLE`.pk_a AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_for_all_columns_with_alias_table_and_alias_clause(self):
        ci = ClauseInfoMySQL(A, A, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query(DIALECT), "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_Clause_for_all_columns_with_asterisk_with_alias_table_and_alias_clause(self):
        ci = ClauseInfoMySQL(A, "*", "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
        self.assertEqual(ci.query(DIALECT), "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`")

    def test_passing_aggregation_method(self):
        ci = ST_AsText(A.data_a, alias_clause="cast_point", dialect=DIALECT)
        self.assertEqual(ci.query(DIALECT), "ST_AsText(a.data_a) AS `cast_point`")

    def test_passing_aggregation_method_with_alias_inside_of_the_method(self):
        ci = ST_AsText(A.data_a, alias_table="new_table", dialect=DIALECT)
        self.assertEqual(ci.query(DIALECT), "ST_AsText(`new_table`.data_a) AS `data_a`")

    @parameterized.expand(
        (
            (func.Max, "max", DIALECT),
            (func.Min, "min", DIALECT),
            (func.Sum, "sum", DIALECT),
        )
    )
    def test_max_function(self, fn: Type[AggregateFunctionBase], result: str, dialect: Dialect):
        ci = fn(A.data_a, context=ClauseInfoContext(table_context={A: "new_table"}), dialect=dialect)
        self.assertEqual(ci.query(DIALECT), f"{result.upper()}(`new_table`.data_a) AS `{result}`")

    def test_max_function_with_clause_alias(self):
        ci = func.Max(A.data_a, alias_clause="alias-clause", dialect=DIALECT)
        self.assertEqual(ci.query(DIALECT), "MAX(a.data_a) AS `alias-clause`")

    def test_passing_aggregation_method_ST_Contains(self):
        comparer = ST_Contains(TableType.points, Point(5, -5), dialect=DIALECT)
        mssg: str = "ST_Contains(ST_AsText(table_type.points), ST_AsText(%s))"
        self.assertEqual(comparer.query(DIALECT), mssg)

    def test_alias_table_property(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_table="{table}~{column}")
        self.assertEqual(ci.alias_table, "a~name_a")

    def test_alias_clause_property(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_clause="{table}~{column}")
        self.assertEqual(ci.alias_clause, "a~name_a")

    def test_alias_clause_property_as_none(self):
        ci = ClauseInfoMySQL(A, A.name_a, alias_table="{table}~{column}")
        self.assertEqual(ci.alias_clause, None)

    @parameterized.expand(
        [
            (ClauseInfoMySQL(A, A), A),
            (ClauseInfoMySQL(None, None), NoneType),
            (ClauseInfoMySQL(A, A.data_a), str),
            (ClauseInfoMySQL(A, A.pk_a), int),
            (ClauseInfoMySQL(A, A.name_a), str),
            (ClauseInfoMySQL(A, A.data_a), str),
            (ClauseInfoMySQL(A, A.date_a), datetime),
            (ClauseInfoMySQL(A, A.value), str),
        ]
    )
    def test_dtype(self, clause_info: ClauseInfo, result: Any) -> None:
        self.assertEqual(clause_info.dtype, result)

    def test_random_value(self):
        ci = ClauseInfoMySQL(None, "random_value")
        self.assertEqual(ci.query(DIALECT), "'random_value'")

    def test_pass_None(self):
        ci = ClauseInfoMySQL(None, None)
        self.assertEqual(ci.query(DIALECT), "NULL")

    def test_pass_float(self):
        ci = ClauseInfoMySQL(None, 3.1415)
        self.assertEqual(ci.query(DIALECT), "3.1415")

    def test_integer_in_column(self):
        ci = ClauseInfoMySQL(None, 20)
        self.assertEqual(ci.query(DIALECT), "20")

    def test_all_None(self):
        self.assertEqual(ClauseInfoMySQL(None, None).query(DIALECT), "NULL")

    def test_raise_NotKeysInIAggregateError(self) -> None:
        with self.assertRaises(NotKeysInIAggregateError) as err:
            ST_AsText(A.data_a, alias_clause="{table}~{column}", dialect=DIALECT).query(DIALECT)
        mssg: str = "We cannot use placeholders in IAggregate class. You used ['table', 'column']"
        self.assertEqual(mssg, err.exception.__str__())

    def test_raise_NotKeysInIAggregateError_with_one_placeholder(self) -> None:
        with self.assertRaises(NotKeysInIAggregateError) as err:
            ST_AsText(A.data_a, alias_clause="{table}", dialect=DIALECT).query(DIALECT)
        mssg: str = "We cannot use placeholders in IAggregate class. You used ['table']"
        self.assertEqual(mssg, err.exception.__str__())

    def test_pass_fk(self) -> None:
        ci = ClauseInfoMySQL(C.B, C.B)
        self.assertEqual(ci.query(DIALECT), "b.pk_b, b.data_b, b.fk_a, b.data")


class TestContextClauseInfo(unittest.TestCase):
    def test_context(self):
        context = ClauseInfoContext()
        ci_parent_dataC = ClauseInfoMySQL(
            table=C,
            column=C.data_c,
            alias_table="alias-for-{table}",
            alias_clause="{column}~alias",
            context=context,
        )
        ci_column_dataC = ClauseInfoMySQL(C, C.data_c, context=context)
        ci_table = ClauseInfoMySQL(C, C, context=context)

        ci_column_fkB_with_alias_clause = ClauseInfoMySQL(C, C.fk_b, alias_clause="{column}-random", context=context)

        self.assertEqual(ci_column_fkB_with_alias_clause.alias_clause, "fk_b-random")
        self.assertEqual(ci_parent_dataC.alias_table, "alias-for-c")
        self.assertEqual(ci_parent_dataC.alias_table, ci_table.alias_table)

        self.assertEqual(ci_parent_dataC.alias_clause, "data_c~alias")
        self.assertEqual(ci_parent_dataC.alias_clause, ci_column_dataC.alias_clause)

    def test_table_context(self) -> None:
        context = ClauseInfoContext()
        parent = ClauseInfoMySQL(C, None, alias_table="my-custom-{table}-table", context=context)
        child = ClauseInfoMySQL(C, C.data_c, alias_clause="{table}", context=context)
        child_with_his_own_alias = ClauseInfoMySQL(C, alias_table="other-alias", context=context)

        self.assertEqual(child.alias_clause, "c")
        self.assertEqual(child.alias_table, parent.alias_table)
        self.assertEqual(child_with_his_own_alias.alias_table, parent.alias_table)

    def test_use_context_even_if_clause_is_not_specified(self) -> None:
        context = ClauseInfoContext()
        parent = ClauseInfoMySQL(C, alias_table="my-custom-alias", context=context)

        child = ClauseInfoMySQL(C, context=context)

        self.assertEqual(parent.alias_table, "my-custom-alias")
        self.assertEqual(parent.alias_table, child.alias_table)

    def test_alias_clause_NULL_when_no_column_is_specified(self):
        self.assertEqual(ClauseInfoMySQL(A).column, "%s")


if __name__ == "__main__":
    unittest.main()
