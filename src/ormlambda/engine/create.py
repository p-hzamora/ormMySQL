from __future__ import annotations
from typing import Any

from ormlambda.engine.url import URL, make_url

from . import base


def create_engine(url: URL | str, **kwargs: Any) -> base.Engine:
    # create url.URL object
    u = make_url(url)
    url, kwargs = u._instantiate_plugins(kwargs)

    entrypoint = u._get_entrypoint()
    dialect_cls = entrypoint.get_dialect_cls()

    dialect_args = {}
    dialect_args["dbapi"] = dialect_cls.import_dbapi()

    dialect = dialect_cls(**dialect_args)
    return base.Engine(dialect, u)
