from typing import Optional, Sequence
from ormlambda.engine.url import URL
from ormlambda.repository.base_repository import BaseRepository
from test.env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_DATABASE,
    DATABASE_URL,
)

from ormlambda.databases.my_sql.types import MySQLArgs
from ormlambda import create_engine

config_dict: MySQLArgs = {
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_DATABASE,
}


def create_engine_for_db(database: str, query: Optional[dict[str, str | Sequence[str]]] = None) -> BaseRepository:
    url = URL.create("mysql", username=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=database, query=query)
    return create_engine(url)


def create_sakila_engine():
    return create_engine_for_db("sakila")


def create_env_engine():
    return create_engine(DATABASE_URL)
