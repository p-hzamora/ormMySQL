from ormlambda.engine import Engine

from test.conftest import config_dict


def test_initialize_MySQLRepository_with_kwargs(sakila_engine: Engine) -> None:  # noqa: F811
    ddbb = sakila_engine.repository

    assert ddbb.database == config_dict["database"]
    assert ddbb.database == config_dict["database"]

    assert ddbb._pool._cnx_config["user"] == config_dict["user"]
    assert ddbb._pool._cnx_config["password"] == config_dict["password"]
    assert ddbb._pool._cnx_config["host"] == config_dict["host"]
