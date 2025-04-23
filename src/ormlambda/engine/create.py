from typing import Any

from ormlambda.engine.url import URL, make_url
from ormlambda import BaseRepository


def create_engine(url: URL | str, **kwargs: Any) -> BaseRepository:
    from ormlambda.databases import MySQLRepository
    from ormlambda.databases import SQLiteRepository

    # create url.URL object
    u = make_url(url)
    url, kwargs = u._instantiate_plugins(kwargs)

    repo_selector = {
        "mysql": MySQLRepository,
        "sqlite": SQLiteRepository,
    }

    if url.drivername not in repo_selector:
        raise ValueError(f"drivername '{url.drivername}' not expected to load Repository class")

    default_config = {
        "user": url.username,
        "password": url.password,
        "host": url.host,
        "database": url.database,
        **kwargs,
    }

    if url.port:
        try:
            default_config["port"] = int(url.port)
        except ValueError:
            raise ValueError(f"The port must be an int. '{url.port}' passed.")

    return repo_selector[url.drivername](**default_config)
