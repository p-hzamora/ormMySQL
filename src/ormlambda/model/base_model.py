from __future__ import annotations


from typing import TYPE_CHECKING, Type

from ormlambda.statements import Statements
from ormlambda.engine import Engine

if TYPE_CHECKING:
    from ormlambda.statements.interfaces import IStatements


class BaseModel[T]:
    """
    This class contains those methods to make query to a table
    """

    def __new__(cls, model: Type[T], engine: Engine) -> IStatements[T]:
        if engine is None:
            raise ValueError("`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class")

        if not isinstance(engine, Engine):
            raise ValueError(f"`{engine}` is not a valid `Engine` instance")

        return Statements(model, engine)


ORM = BaseModel
