from __future__ import annotations
from typing import Callable
import pytest


from ormlambda import ORM
from ormlambda import Engine
from ormlambda import IStatements
from ormlambda.common.errors import UnmatchedLambdaParameterError

from test.models import TableType


DB_NAME = "__test_ddbb__"

MSSG_ERROR: str = "Unmatched number of parameters in lambda function with the number of tables: Expected 1 parameters but found ('x', 'y', 'z')."


# DEPRECATED
@pytest.fixture
def setUp(engine_no_db: Engine, create_engine_for_db: Callable[[str], Engine]):
    engine_no_db.create_schema(DB_NAME, "replace")
    engine = create_engine_for_db(DB_NAME)

    model = ORM(TableType, engine)
    model.create_table("replace")
    yield model
    engine.drop_schema(DB_NAME)


@pytest.mark.skip("Depricated")
def test_UnmatchedLambdaParameterError_in_where(model: IStatements[TableType]):
    with pytest.raises(UnmatchedLambdaParameterError) as err:
        model.where(lambda x, y, z: x.points == 2).select_one(lambda x: x.points, flavour=tuple)

    assert MSSG_ERROR == str(err.value)


@pytest.mark.skip("Depricated")
def test_UnmatchedLambdaParameterError_in_select_one(model: IStatements[TableType]):
    with pytest.raises(UnmatchedLambdaParameterError) as err:
        model.select_one(lambda x, y, z: x.points, flavour=tuple)

    assert MSSG_ERROR == str(err.value)


@pytest.mark.skip("Depricated")
def test_UnmatchedLambdaParameterError_in_select(model: IStatements[TableType]):
    with pytest.raises(UnmatchedLambdaParameterError) as err:
        model.select(lambda x, y, z: x.points, flavour=tuple)

    assert MSSG_ERROR == str(err.value)
