from typing import Callable, cast
import pytest
from ormlambda.engine import Engine
from test.env import DATABASE_URL, DB_PREFIX

from ormlambda import create_engine, URL, make_url, IStatements, ORM
from test.models import Address


def pytest_collection_modifyitems(config, items):
    """Skip all test files with 'query' in their filename"""
    skip_query = pytest.mark.skip(reason="Skipping test files with 'query' in filename")
    for item in items:
        if "query" in cast(str,item.nodeid).lower().split("::")[0]:
            item.add_marker(skip_query)


_URL = make_url(DATABASE_URL)

DB_USERNAME = _URL.username
DB_PASSWORD = _URL.password
DB_HOST = _URL.host
DB_PORT = _URL.port
DB_DATABASE = _URL.database

config_dict = {
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_DATABASE,
}


@pytest.fixture(scope="session")
def create_engine_for_db() -> Callable[[str], Engine]:
    def create_real_engine(database: str, **kwargs) -> Engine:
        url = URL.create(
            _URL.drivername,
            username=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=database,
            **kwargs,
        )
        return create_engine(url)

    return create_real_engine


@pytest.fixture(scope="session")
def engine_no_db():
    return create_engine(f"{DB_PREFIX}{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}")


@pytest.fixture(scope="session")
def sakila_engine(create_engine_for_db) -> Engine:
    return create_engine_for_db("sakila")


@pytest.fixture(scope="package")
def amodel(sakila_engine) -> IStatements[Address]:  # noqa: F811
    return ORM(Address, sakila_engine)
