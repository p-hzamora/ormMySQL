from pathlib import Path
from typing import Callable
import pytest
import subprocess
from ormlambda.engine import Engine
from test.env import DATABASE_URL, DB_PREFIX, TEST_DIR

from ormlambda import create_engine, URL, make_url, IStatements, ORM
from test.models import Address


def pytest_collection_modifyitems(config, items: list[pytest.Item]):
    """Skip all test files with 'query' in their filename"""
    skip_query = pytest.mark.skip(reason="Skipping test files with 'query' in filename")
    for item in items:
        if "query" in Path(item.location[0]).stem:
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


@pytest.fixture(scope="session", autouse=True)
def create_mysql_sakila_db(engine_no_db: Engine):
    SAKILA = "sakila"
    if not engine_no_db.schema_exists(SAKILA):
        # Get the path to the SQL file
        sql_file_path = TEST_DIR / "schema" / "sakila-db.sql"

        # Build mysql command: mysql -u user -ppassword -h host -P port < file.sql
        mysql_cmd = ["mysql", "-u", DB_USERNAME]

        if DB_PASSWORD:
            mysql_cmd.append(f"-p{DB_PASSWORD}")

        mysql_cmd.extend(["-h", DB_HOST, "-P", str(DB_PORT)])

        # Execute the SQL file
        with open(sql_file_path, "r") as sql_file:
            subprocess.run(mysql_cmd, stdin=sql_file, check=True)

    yield

    engine_no_db.drop_schema(SAKILA)


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
