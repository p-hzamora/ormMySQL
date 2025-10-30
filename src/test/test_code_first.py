import pytest


# Custom libraries
from test.models import Country  # noqa: E402
from ormlambda import ORM, IStatements
from ormlambda.engine import Engine

DB_NAME = "__test_ddbb__"


@pytest.fixture(scope="module", autouse=True)
def create_and_drop_schema(engine_no_db: Engine):
    """Create test schema, yield, then drop it"""
    engine_no_db.create_schema(DB_NAME, "replace")
    yield
    engine_no_db.drop_schema(DB_NAME, if_exists=True)


@pytest.fixture(scope="module")
def engine(create_engine_for_db):
    """Engine connected to test database"""
    return create_engine_for_db(DB_NAME)


@pytest.fixture(scope="module")
def repository(base_engine: Engine):
    """Database repository for code-first operations"""
    return base_engine.repository


@pytest.fixture(scope="module")
def country_model(engine) -> IStatements[Country]:
    """ORM model for Country table"""
    return ORM(Country, engine)


def test_create_table(country_model: IStatements[Country]):
    """Test creating a table"""
    if country_model.table_exists():
        country_model.drop_table()

    country_model.create_table()
    assert country_model.table_exists()


@pytest.mark.skip(reason="FIXME: refactor to fix and include this method")
def test_create_table_code_first_passing_folder(repository):
    """Test creating tables from folder"""
    repository.create_tables_code_first("src/test/models")


@pytest.mark.skip(reason="FIXME: refactor to fix and include this method")
def test_create_table_code_first_passing_file(repository):
    """Test creating tables from file"""
    repository.create_tables_code_first("src/test/models/models_in_the_same_file/all_models_in_one_file.py")
