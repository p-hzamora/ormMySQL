from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ormlambda.common.interfaces import (
        IRepositoryBase,
        IStatements,
        ICaster,
    )


class Template[TCnx]:
    repository: IRepositoryBase[TCnx]
    caster: ICaster
    statement: IStatements


class RepositoryTemplateDict[TRepo]:
    _instance: Optional[RepositoryTemplateDict[TRepo]] = None

    def __new__[T: Template](cls):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        from .databases.my_sql import (
            MySQLCaster,
            MySQLRepository,
            MySQLStatements,
        )

        class MySQLTemplate[TCnx](Template[TCnx]):
            repository = MySQLRepository
            caster = MySQLCaster
            statement = MySQLStatements

        class MariaTemplate[TCnx](Template[TCnx]): ...

        # FIXME [ ]: should return T instead of Template
        cls._data: dict[IRepositoryBase[TRepo], Template] = {
            MySQLRepository: MySQLTemplate,
            MariaTemplate: ...,
        }

        return cls._instance

    # FIXME [ ]: should return T instead of Template
    def get[T: Template](self, key: IRepositoryBase[TRepo]) -> Template:
        key = key if isinstance(key,type) else type(key)
        return self._instance._data[key]
