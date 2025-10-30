from datetime import datetime

import pytest

from test.models import (
    Address,
    City,
    Country,
)
from ormlambda.sql.comparer import Comparer
from ormlambda.common import GlobalChecker
from ormlambda.dialects import mysql
from ormlambda import IStatements, ORM
from test.models import A, TableType
from shapely import Point


DIALECT = mysql.dialect


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


def test_one_where(amodel: IStatements[Address]):
    string = amodel.where(lambda x: x.address == 10).query("where")
    assert string == "WHERE `address`.address = 10"


def test_multiples_where(amodel: IStatements[Address]):
    # fmt: off
    string = (
        amodel
        .where(lambda x: 
            (
                x.address == "madrid",
                x.address2 == "other",
                x.district == 1000,
                x.city_id == 87,
            ),
        )
        .where(lambda x: x.last_update >= datetime(2025,12,16),restrictive=False)
        .where(lambda x: ((x.City.city_id==1) | (x.City.Country.country != 'Spain') & (x.City.city_id == 124)),restrictive=True)
        .query("where")
    )
    # fmt: on
    mssg = "WHERE `address`.address = 10 AND (`address`.address = 'madrid' AND `address`.address2 = 'other' AND `address`.district = 1000 AND `address`.city_id = 87) OR `address`.last_update >= '2025-12-16 00:00:00' AND (`address_City`.city_id = 1 OR `address_City_Country`.country != 'Spain' AND `address_City`.city_id = 124)"
    assert string == mssg


def test_where_with_different_table_base(amodel: IStatements[Address]):
    string = amodel.where(
        lambda x: (
            x.address == "sol",
            x.City.city == "Madrid",
        ),
    ).query("where")

    assert string == "WHERE (`address`.address = 'sol' AND `address_City`.city = 'Madrid')"


def test_passing_multiples_wheres_combining_AND_OR(amodel: IStatements[Address]) -> None:
    # fmt: off
    string = (
        amodel
        .where(lambda x: (x.City.Country.country.regex("^[Ss]")) & (x.City.city.like("%(%")) & (x.city_id != 388))
        .where(lambda x: x.City.city == "Madrid",False)
        .query('where')
    )

    EXPECTED = "WHERE (`address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388) OR `address_City`.city = 'Madrid'"
    assert string == EXPECTED
    # fmt: on


def test_passing_multiples_wheres_combining_AND_OR_using_other_approach(amodel: IStatements[Address]) -> None:
    # fmt: off
    string = (
        amodel
        .where(lambda x: (
                x.City.Country.country.regex("^[Ss]"),
                x.City.city.like("%(%"),
                x.city_id != 388
            )
        )
        .where(lambda x: x.City.city == "Madrid",False)
        .query('where')
    )

    EXPECTED = "WHERE (`address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388) OR `address_City`.city = 'Madrid'"
    assert string == EXPECTED
    # fmt: on


def test_passing_multiples_wheres_clauses(amodel: IStatements[Address]) -> None:
    # fmt: off
    string = (
        amodel
        .where(lambda x: x.City.Country.country.regex("^[Ss]"))
        .where(lambda x: x.City.city.like("%(%"))
        .where(lambda x: x.city_id != 388)
        .where(lambda x: x.City.city == "Madrid", False)
        .query('where')
    )

    EXPECTED = "WHERE `address_City_Country`.country REGEXP '^[Ss]' AND `address_City`.city LIKE '%(%' AND `address`.city_id != 388 OR `address_City`.city = 'Madrid'"
    assert string == EXPECTED
    # fmt: on


def test_where_with_different_tables_recursive(amodel: IStatements[Address]):
    address = "sol"
    city = "Madrid"
    country = "Spain"
    string = amodel.where(
        lambda x: (
            x.address == address,
            x.City.city == city,
            x.City.Country.country == country,
        )
    ).query("where")
    assert string == "WHERE (`address`.address = 'sol' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain')"


def test_where_with_regex(amodel: IStatements[Address]):
    pattern: str = r"^[A+]"
    string = amodel.where(lambda x: x.address.regex(pattern)).query("where")
    assert string == f"WHERE `address`.address REGEXP '{pattern}'"


def test_where_with_like(amodel: IStatements[Address]):
    pattern: str = r"*123*"
    string = amodel.where(lambda x: x.address.like(pattern)).query("where")
    assert string == f"WHERE `address`.address LIKE '{pattern}'"


def test_where_contains(amodel: IStatements[Address]):
    string = amodel.where(lambda x: x.address_id.contains((1, 2, 3, 4, 5, 6, 7, 8, 9))).query("where")
    assert string == "WHERE `address`.address_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)"


def test_where_not_contains(amodel: IStatements[Address]):
    string = amodel.where(lambda x: x.address_id.not_contains((1, 2, 3, 4, 5, 6, 7, 8, 9))).query("where")
    assert string == "WHERE `address`.address_id NOT IN (1, 2, 3, 4, 5, 6, 7, 8, 9)"


ADDRESS_1 = Address(200, "Calle Cristo de la victoria", "Usera", None, 1, "28026", "617128992", None, None)


def test_value_replace_2(amodel: IStatements[Address]):
    country = Country(50, "Espanna")

    string = amodel.where(lambda x: (ADDRESS_1.city_id != x.City.city_id) & (x.City.city_id <= country.country_id)).query("where")
    assert string == "WHERE (`address_City`.city_id != 1 AND `address_City`.city_id <= 50)"


def test_like_condition(amodel: IStatements[Address]):
    country = Country(50, "Espanna")

    string = amodel.where(lambda x: x.city_id.regex(country.country)).query("where")
    assert string == "WHERE `address`.city_id REGEXP 'Espanna'"


def test_comparer() -> None:
    cond = GlobalChecker.resolved_callback_object(A, lambda x: x.pk_a == 100)[0]
    assert isinstance(cond, Comparer)  # noqa: F821


def test_simple_condition():
    comparer = GlobalChecker[City].resolved_callback_object(City, lambda x: x.last_update >= datetime(2024, 1, 16))[0]
    mssg: str = "`city`.last_update >= '2024-01-16 00:00:00'"
    assert comparer.compile(DIALECT).string, mssg


def test_condition_with_and_and_or():
    # fmt: off
    comparer = GlobalChecker[City].resolved_callback_object(City, lambda x: (
        x.last_update >= datetime(2024, 1, 16)) & 
        (x.city_id <= 100) | 
        (x.Country.country == "asdf"))[0]  # noqa: F821
    # fmt: on
    EXPECTED: str = "`city`.last_update >= '2024-01-16 00:00:00' AND `city`.city_id <= 100 OR `city_Country`.country = 'asdf'"
    query = comparer.compile(DIALECT).string
    assert query == EXPECTED


@pytest.mark.skip("# FIXME [ ]: Currently returns 'WHERE ST_AsText(`table_type`.points) IN ST_AsText(%s)' ")
def test_condition_with_ST_Contains(engine_no_db):
    string = ORM(TableType, engine_no_db).where(lambda x: x.points.contains(Point(5, -5))).query("where")
    mssg: str = "WHRE ST_Contains(ST_AsText(`table_type`.points), ST_AsText(%s))"
    assert string == mssg


def test_retrieve_string_from_class_property_using_variable():
    VAR = 10
    compare = GlobalChecker[Address].resolved_callback_object(Address, lambda x: x.city_id == VAR)[0]
    assert compare.compile(DIALECT).string, "`address`.city_id = 10"


def test_join_some_Comparer_object_using_column_proxy(amodel: IStatements[Address]) -> None:
    VAR = "Madrid"

    string = amodel.where(
        lambda x: (
            x.address == "Tetuan",
            x.City.city == VAR,
            x.City.Country.country == "Spain",
        )
    ).query("where")

    assert string == "WHERE (`address`.address = 'Tetuan' AND `address_City`.city = 'Madrid' AND `address_City_Country`.country = 'Spain')"
