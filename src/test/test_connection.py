from ormlambda import create_engine


def test_connection_default():
    engine = create_engine("mysql://root:1500@localhost:3306?")

    assert repr(engine) == "Engine: mysql://root:***@localhost:3306"

    assert engine.repository.pool.pool_size == 5
    assert engine.repository.database is None


def test_connection_():
    engine = create_engine("mysql://root:1500@localhost:3306/sakila?pool_size=20")

    assert repr(engine) == "Engine: mysql://root:***@localhost:3306/sakila?pool_size=20"

    assert engine.repository.pool.pool_size == 20
    assert engine.repository.database == "sakila"
