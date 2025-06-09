from __future__ import annotations


from typing import TYPE_CHECKING, Type

from ormlambda.statements import Statements
from ormlambda.engine import Engine

if TYPE_CHECKING:
    from ormlambda.statements.interfaces import IStatements_two_generic


# endregion


class BaseModel[T]:
    """
    Class to select the correct BaseStatement class depends on the repository.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    # region Constructor

    def __new__[TPool](cls, model: Type[T], engine: Engine) -> IStatements_two_generic[T, TPool]:
        if engine is None:
            raise ValueError("`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class")

        if not isinstance(engine, Engine):
            raise ValueError(f"`{engine}` is not a valid `Engine` instance")

        return Statements(model, engine)


ORM = BaseModel
