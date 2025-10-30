from __future__ import annotations
from datetime import datetime
from types import NoneType
from typing import Annotated, Any, TYPE_CHECKING, Type, cast
import pytest
from shapely import Point


from ormlambda.common.global_checker import GlobalChecker
from ormlambda.sql.elements import ClauseElement

if TYPE_CHECKING:
    from ormlambda.dialects import Dialect
from ormlambda.common.errors import NotKeysInIFunctionError
from ormlambda.dialects.mysql.clauses.ST_AsText import ST_AsText
from ormlambda.dialects.mysql.clauses.ST_Contains import ST_Contains
from ormlambda.sql.clause_info import ClauseInfo

from ormlambda.sql import functions as func
from ormlambda import ColumnProxy
from test.models import A, C, TableType
from ormlambda.dialects import mysql
from ormlambda import Table, PrimaryKey, INT, VARCHAR, Column

DIALECT = mysql.dialect


class TableTest(Table):
    __table_name__ = "__ddbb__.new_table"

    pk_table: Annotated[Column[INT], PrimaryKey()]
    data_1: Annotated[Column[VARCHAR], VARCHAR(10)]
    data_2: Annotated[Column[VARCHAR], VARCHAR(20)]
    data_3: Annotated[Column[VARCHAR], VARCHAR(30)]


@pytest.fixture
def make_ClauseInfo() -> Type[ClauseInfo]:
    def create_clause_info(*args, **kwargs) -> Type[ClauseInfo]:
        return ClauseInfo(*args, **kwargs, dialect=DIALECT)

    return create_clause_info


@pytest.mark.xfail(reason="Known issue - added backticks around 'a' when they weren't needed")
def test_passing_only_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, alias_clause="{table}")
    query = ci.query(DIALECT)
    assert query == "`a`"


@pytest.mark.parametrize(
    "table,column,result",
    (
        (A, "name", "name"),
        (None, "name", "'name'"),
    ),
)
def test_column_property(make_ClauseInfo, table, column, result):
    ci = make_ClauseInfo(table, column)
    assert ci.column == result


def test_passing_only_table_with_alias_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, alias_table=lambda x: "custom_table_name", first_apperance=True)
    query = ci.query(DIALECT)
    assert query == "a AS `custom_table_name`"


def test_passing_only_table_with_alias_table_placeholder_of_column(make_ClauseInfo):
    with pytest.raises(ValueError) as err:
        make_ClauseInfo(A, alias_table=lambda x: "{column}").query(DIALECT)

    mssg = "You cannot use {column} placeholder without using 'column' attribute"
    assert str(err.value) == mssg


@pytest.mark.skip(reason="This test is no longer needed")
def test_passing_only_column_with_alias_table_placeholder_of_table(make_ClauseInfo):
    with pytest.raises(ValueError) as err:
        make_ClauseInfo(None, "random_value", alias_clause=lambda x: "{table}").query(DIALECT)

    mssg = "You cannot use {table} placeholder without using 'table' attribute"
    assert str(err.value) == mssg


def test_passing_only_table_with_alias_table_placeholder_of_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, alias_table=lambda x: "{table}", first_apperance=True)
    query = ci.query(DIALECT)
    assert query == "a AS `a`"


def test_constructor(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.pk_a)
    query = ci.query(DIALECT)
    assert query == "a.pk_a"


def test_passing_callable_alias_clause(make_ClauseInfo):
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.name_a)[0]
    ci = make_ClauseInfo(A, column_proxy, alias_clause=lambda x: "resolver_with_lambda_{column}")
    query = ci.query(DIALECT)
    assert query == "a.name_a AS `resolver_with_lambda_name_a`"


def test_passing_string_with_placeholder_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.name_a, alias_clause="resolver_with_lambda_{column}")
    query = ci.query(DIALECT)
    assert query == "a.name_a AS `resolver_with_lambda_name_a`"


def test_passing_callable_alias_clause_with_placeholder(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.name_a, alias_clause=lambda x: "resolver_with_lambda_{table}")
    query = ci.query(DIALECT)
    assert query == "a.name_a AS `resolver_with_lambda_a`"


@pytest.mark.parametrize(
    "column,string_col,result",
    (
        (A.pk_a, "pk_a", int),
        (A.name_a, "name_a", str),
        (A.data_a, "data_a", str),
        (A.date_a, "date_a", datetime),
        (A.value, "value", str),
    ),
)
def test_passing_callable_and_custom_method(make_ClauseInfo, column, string_col: str, result: object):
    def message_placeholder(ci: ColumnProxy):
        return ci.dtype.python_type.__name__

    ci = make_ClauseInfo(A, column, alias_clause=message_placeholder)
    query = ci.query(DIALECT)
    assert query == f"a.{string_col} AS `{result.__name__}`"


@pytest.mark.parametrize(
    "column,string_col,result",
    (
        (A.pk_a, "pk_a", "INTEGER"),
        (A.name_a, "name_a", "TEXT"),
        (A.data_a, "data_a", "TEXT"),
        (A.date_a, "date_a", "DATETIME"),
        (A.value, "value", "TEXT"),
    ),
)
def test_custom_message_placeholder(make_ClauseInfo, column, string_col: str, result: object):
    def message_placeholder(ci: ClauseInfo):
        return f"{str(ci.dtype)}~" + "{column}"

    ci = make_ClauseInfo(A, column, alias_clause=message_placeholder)
    query = ci.query(DIALECT)
    assert query == f"a.{string_col} AS `{result}~{string_col}`"


def test_passing_callable_alias_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.date_a, alias_table=lambda x: "custom_alias_for_{table}_table")
    query = ci.query(DIALECT)
    assert query == "`custom_alias_for_a_table`.date_a"


def test_passing_placeholder_as_alias(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.date_a, alias_table="{table}")
    query = ci.query(DIALECT)
    assert query == "`a`.date_a"


def test_call_A_withou_alias(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.date_a)
    query = ci.query(DIALECT)
    assert query == "a.date_a"


def test_passing_callable_alias_table_with_placeholder(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.date_a, alias_table=lambda x: "custom_alias_for_{column}_column")
    query = ci.query(DIALECT)
    assert query == "`custom_alias_for_date_a_column`.date_a"


def test_passing_asterisk(make_ClauseInfo):
    ci = make_ClauseInfo(A, "*")
    query = ci.query(DIALECT)
    assert query == "a.pk_a, a.name_a, a.data_a, a.date_a, a.value"


def test_hardcoding_asterisk(make_ClauseInfo):
    ci = make_ClauseInfo(A, "*", keep_asterisk=True)
    query = ci.query(DIALECT)
    assert query == "a.*"


def test_hardcoding_asterisk_with_alias_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, "*", alias_table="new_name", keep_asterisk=True)
    query = ci.query(DIALECT)
    assert query == "`new_name`.*"


def test_passing_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, A)
    query = ci.query(DIALECT)
    assert query == "a.pk_a, a.name_a, a.data_a, a.date_a, a.value"


def test_passing_alias_table(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.data_a, "ALIAS_TABLE")
    query = ci.query(DIALECT)
    assert query == "`ALIAS_TABLE`.data_a"


def test_passing_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.data_a, None, "ALIAS_FOR_ALL_CLAUSE")
    query = ci.query(DIALECT)
    assert query == "a.data_a AS `ALIAS_FOR_ALL_CLAUSE`"


def test_Clause_with_alias_table_and_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(A, A.pk_a, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
    query = ci.query(DIALECT)
    assert query == "`ALIAS_TABLE`.pk_a AS `ALIAS_FOR_ALL_CLAUSE`"


def test_Clause_for_all_columns_with_alias_table_and_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(A, A, "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
    query = ci.query(DIALECT)
    assert query == "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`"


def test_Clause_for_all_columns_with_asterisk_with_alias_table_and_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(A, "*", "ALIAS_TABLE", "ALIAS_FOR_ALL_CLAUSE")
    query = ci.query(DIALECT)
    assert query == "`ALIAS_TABLE`.* AS `ALIAS_FOR_ALL_CLAUSE`"


def test_passing_aggregation_method():
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]
    ci = ST_AsText(column_proxy, alias="cast_point")
    assert ci.compile(DIALECT).string == "ST_AsText(`a`.data_a) AS `cast_point`"


def test_passing_aggregation_method_with_alias_inside_of_the_method():
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]
    ci = ST_AsText(column_proxy, alias="alias-for-clause")
    assert ci.compile(DIALECT).string == "ST_AsText(`a`.data_a) AS `alias-for-clause`"


@pytest.mark.parametrize(
    "fn,result,dialect",
    (
        (func.Max, "max", DIALECT),
        (func.Min, "min", DIALECT),
        (func.Sum, "sum", DIALECT),
    ),
)
def test_max_function(fn: Type[ClauseElement], result: str, dialect: Dialect):
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]
    ci = fn(column_proxy)
    assert ci.compile(dialect).string == f"{result.upper()}(`a`.data_a) AS `{result}`"


def test_max_function_with_clause_alias():
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]

    ci = func.Max(column_proxy, "alias-clause")
    assert ci.compile(DIALECT).string == "MAX(`a`.data_a) AS `alias-clause`"


@pytest.mark.skip(reason="This test shouldn't be here")
def test_passing_aggregation_method_ST_Contains():
    column_proxy = GlobalChecker.resolved_callback_object(TableType, lambda x: cast(TableType, x).points)[0]
    comparer = ST_Contains(column_proxy, Point(5, -5))
    mssg: str = "ST_Contains(ST_AsText(`table_type`.points), ST_AsText(%s))"
    assert comparer.compile(DIALECT).string == mssg


def test_alias_table_property(make_ClauseInfo):
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.name_a)[0]
    ci = make_ClauseInfo(A, column_proxy, alias_table="{table}~{column}")
    assert ci.alias_table == "a~name_a"


def test_alias_clause_property(make_ClauseInfo):
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.name_a)[0]
    ci = make_ClauseInfo(A, column_proxy, alias_clause="{table}~{column}")

    query = ci.query(DIALECT)
    assert query == "a.name_a AS `a~name_a`"


def test_alias_clause_property_as_none(make_ClauseInfo):
    column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.name_a)[0]
    ci = make_ClauseInfo(A, column_proxy, alias_table="{table}~{column}")
    assert ci.alias_clause is None


@pytest.mark.slow
@pytest.mark.parametrize(
    "clause_info_attrs,result",
    [
        ((A, A), A),
        ((None, None), NoneType),
        ((A, A.data_a), str),
        ((A, A.pk_a), int),
        ((A, A.name_a), str),
        ((A, A.data_a), str),
        ((A, A.date_a), datetime),
        ((A, A.value), str),
    ],
)
def test_dtype(make_ClauseInfo, clause_info_attrs: ClauseInfo, result: Any) -> None:
    clause = make_ClauseInfo(*clause_info_attrs)
    assert clause.dtype == result


def test_random_value(make_ClauseInfo):
    ci = make_ClauseInfo(None, "random_value")
    query = ci.query(DIALECT)
    assert query == "'random_value'"


@pytest.mark.skip(reason="I don't know why I created this Test")
def test_pass_None(make_ClauseInfo):
    ci = make_ClauseInfo(None, None)
    query = ci.query(DIALECT)
    assert query == "NULL"


def test_pass_float(make_ClauseInfo):
    ci = make_ClauseInfo(None, 3.1415)
    query = ci.query(DIALECT)
    assert query == "3.1415"


def test_integer_in_column(make_ClauseInfo):
    ci = make_ClauseInfo(None, 20)
    query = ci.query(DIALECT)
    assert query == "20"


def test_raise_NotKeysInIFunctionError() -> None:
    with pytest.raises(NotKeysInIFunctionError) as err:
        column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]
        ST_AsText(column_proxy, alias="{table}~{column}").compile(DIALECT)
    mssg: str = "We cannot use placeholders in IFunction class. You used ['table', 'column']"
    assert mssg == str(err.value)


def test_raise_NotKeysInIFunctionError_with_one_placeholder() -> None:
    with pytest.raises(NotKeysInIFunctionError) as err:
        column_proxy = GlobalChecker.resolved_callback_object(A, lambda x: x.data_a)[0]
        ST_AsText(column_proxy, alias="{table}").compile(DIALECT)
    mssg: str = "We cannot use placeholders in IFunction class. You used ['table']"
    assert mssg == str(err.value)


def test_pass_fk(make_ClauseInfo) -> None:
    ci = make_ClauseInfo(C.B, C.B)
    query = ci.query(DIALECT)
    assert query == "b.pk_b, b.data_b, b.fk_a, b.data"


@pytest.mark.skip(reason="I don't know yet why should it return '%s' instead None")
def test_alias_clause_NULL_when_no_column_is_specified(make_ClauseInfo):
    assert make_ClauseInfo(A).column == "%s"


@pytest.fixture
def make_TableTest():
    def compose_TableTest(*args, **kwargs):
        return TableTest(*args, **kwargs)

    return compose_TableTest


def test_split_db_name_for_table_name(make_ClauseInfo):
    col = GlobalChecker[TableTest].resolved_callback_object(TableTest, lambda x: x.data_1)[0]

    assert make_ClauseInfo(TableTest, col).query(DIALECT) == "`__ddbb__`.`new_table`.data_1"


def test_show_db_passing_table(make_ClauseInfo):
    ci = make_ClauseInfo(TableTest)

    string = ci.query(DIALECT)

    assert string == "`__ddbb__`.`new_table`"


def test_show_db_passing_alias_clause(make_ClauseInfo):
    ci = make_ClauseInfo(TableTest, alias_table="{table}", first_apperance=True)

    string = ci.query(DIALECT)

    assert string == "`__ddbb__`.`new_table` AS `new_table`"


def test_show_db_passing_alias_table(make_ClauseInfo):
    ci = make_ClauseInfo(TableTest, alias_table="name-{table}")

    string = ci.query(DIALECT)

    assert string == "`name-new_table`"
