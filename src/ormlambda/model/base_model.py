from __future__ import annotations


from typing import TYPE_CHECKING, Type

from ormlambda.engine.template import RepositoryTemplateDict

if TYPE_CHECKING:
    from ormlambda.statements.interfaces import IStatements_two_generic
    from ormlambda.repository import BaseRepository


# endregion


class BaseModel[T]:
    """
    Class to select the correct BaseStatement class depends on the repository.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    # region Constructor

    def __new__[TPool](cls, model: Type[T], repository: BaseRepository[TPool]) -> IStatements_two_generic[T, TPool]:
        if repository is None:
            raise ValueError("`None` cannot be passed to the `repository` attribute when calling the `BaseModel` class")

        new_cls = RepositoryTemplateDict().get(repository).statement

        if not new_cls:
            raise Exception(f"The selected repository '{repository}' does not exist.")

        return new_cls(model, repository)


ORM = BaseModel
