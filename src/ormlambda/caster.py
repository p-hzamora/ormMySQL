from __future__ import annotations


from typing import Optional, Type, TYPE_CHECKING, Callable, overload

from ormlambda.utils.global_checker import GlobalChecker
from ormlambda.types import ColumnType
from .template import RepositoryTemplateDict

if TYPE_CHECKING:
    from ormlambda.utils.column import Column
    from ormlambda.common.interfaces import IRepositoryBase, ICaster


PLACEHOLDER: str = "%s"


class CasterResult[TRepo, TProp]:
    def __init__(
        self,
        repository: IRepositoryBase[TRepo],
        column_type: Column[TProp],
        value: TProp,
        is_insert_data: bool = False,
    ):
        self._repository: IRepositoryBase[TRepo] = repository

        self._caster: ICaster = RepositoryTemplateDict[TRepo]().get(repository).caster
        self._column: Column[TProp] = column_type
        self._value: TProp = value
        self._is_insert_data: bool = is_insert_data

    @property
    def from_database(self) -> TProp:
        return self._caster.READ.resolve(self._column, self._value)

    @property
    def wildcard(self) -> str:
        return self._caster.WRITE.resolve(self._column, PLACEHOLDER, insert_data=self._is_insert_data)

    @property
    def select_wildcard(self) -> str:
        return self._caster.WRITE.resolve(self._column, PLACEHOLDER, insert_data=self._is_insert_data)

    @property
    def insert_update_wildcard(self) -> str:
        return self._caster.WRITE.resolve(self._column, PLACEHOLDER, insert_data=self._is_insert_data)

    @property
    def to_query(self) -> str:
        return self._caster.WRITE.resolve(self._column, self._value, insert_data=self._is_insert_data)

    def __getitem__(self, name: str) -> Optional[TProp | str]:
        if hasattr(self, name):
            return getattr(self, name)
        return None

    def writer_resolve[TProp](self, type_value, value: ColumnType[TProp]) -> TProp:
        return self._caster.WRITE.resolve(type_value, value)

    def reader_resolve[TProp](self, type_value, value: ColumnType[TProp]) -> TProp:
        return self._caster.READ.resolve(type_value, value)


class Caster[TRepo, T]:
    @overload
    def __init__(self, repository: IRepositoryBase[TRepo]): ...
    @overload
    def __init__(self, repository: IRepositoryBase[TRepo], instance: T): ...
    @overload
    def __init__(self, repository: IRepositoryBase[TRepo], instance: T, insert: bool): ...

    def __init__(self, repository: IRepositoryBase[TRepo], instance: Optional[T] = None, insert: bool = False):
        self._repository: IRepositoryBase[TRepo] = repository
        self._instance: T = instance
        self._is_insert_data: bool = insert

    @overload
    def for_column[TProp](self, column: Callable[[T], TProp]) -> CasterResult[TRepo, TProp]: ...
    @overload
    def for_column[TProp](self, column: TProp) -> CasterResult[TRepo, TProp]: ...

    def for_column[TProp: ColumnType](self, column: TProp | Callable[[T], TProp]) -> CasterResult[TRepo, TProp]:
        if not self._instance:
            raise ValueError("You must specified an instance variable on the constructor before calling 'for_column' method")
        if GlobalChecker.is_lambda_function(column):
            column_type = column(type(self._instance)).dtype
            column_value = column(self._instance)
        else:
            column_type = column.dtype
            column_value = self._instance[column]

        return CasterResult[TRepo, TProp](self._repository, column_type, column_value, is_insert_data=self._is_insert_data)

    @overload
    def for_value[TProp](self, value: TProp) -> CasterResult[TRepo, TProp]: ...
    @overload
    def for_value[TProp](self, value: TProp, forced_type: Optional[Type[TProp]]) -> CasterResult[TRepo, TProp]: ...

    def for_value[TProp](self, value: TProp, forced_type: Optional[Type[TProp]] = None) -> CasterResult[TRepo, TProp]:
        column_type = forced_type if forced_type else type(value)
        return CasterResult[TRepo, TProp](self._repository, column_type=column_type, value=value, is_insert_data=self._is_insert_data)
