from test.models import City

from ormlambda import ORM


def test_create_table(sakila_engine):
    ORM(City, sakila_engine).create_table("append")
