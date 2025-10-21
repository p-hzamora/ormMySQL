from __future__ import annotations
from ormlambda.engine import create_engine, Engine


from test.env import DB_PASSWORD, DB_USERNAME


def test_create_engine() -> None:
    url_connection = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/sakila?pool_size=3"
    db = create_engine(url_connection)

    assert isinstance(db, Engine)
