from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type

if TYPE_CHECKING:
    from ormlambda.repository import IRepositoryBase
    from ormlambda.statements.interfaces import IStatements
    from ormlambda.caster import ICaster


class Template[TCnx]:
    repository: Type[IRepositoryBase]
    caster: Type[ICaster]
    statement: Type[IStatements]


class RepositoryTemplateDict[TRepo]:
    _instance: Optional[RepositoryTemplateDict[TRepo]] = None

    def __new__[T: Template](cls):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)

        from ..databases.my_sql import (
            MySQLCaster,
            MySQLRepository,
            MySQLStatements,
        )

        class MySQLTemplate[TCnx](Template[TCnx]):
            repository = MySQLRepository
            caster = MySQLCaster
            statement = MySQLStatements

        # FIXME [ ]: should return T instead of Template
        cls._data: dict[IRepositoryBase, Template] = {
            MySQLRepository: MySQLTemplate,
        }

        return cls._instance

    # FIXME [ ]: should return T instead of Template
    def get[T: Template](self, key: IRepositoryBase) -> Template:
        key = key if isinstance(key, type) else type(key)
        return self._instance._data[key]
