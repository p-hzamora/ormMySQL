from typing import Optional, Sequence
from ormlambda.engine import Engine
from test.env import DATABASE_URL

from ormlambda import create_engine, URL, make_url

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


def create_engine_for_db(database: str, query: Optional[dict[str, str | Sequence[str]]] = None) -> Engine:
    url = URL.create(_URL.drivername, username=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=database, query=query)
    return create_engine(url)


def create_sakila_engine() -> Engine:
    return create_engine_for_db("sakila")


def create_env_engine() -> Engine:
    return create_engine(DATABASE_URL)
