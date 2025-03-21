from __future__ import annotations


from typing import Optional, Type, TYPE_CHECKING, Callable, overload

from ormlambda.common.global_checker import GlobalChecker
from ormlambda.sql.types import ColumnType
from ormlambda.engine.template import RepositoryTemplateDict

if TYPE_CHECKING:
    from ormlambda.caster import BaseCaster
    from ormlambda.repository import IRepositoryBase


PLACEHOLDER: str = "%s"


class Caster[TRepo]:
    def __init__(self, repository: IRepositoryBase):
        self._repository: IRepositoryBase = repository
        self._caster = RepositoryTemplateDict().get(repository).caster

    @overload
    def for_column[T, TProp](self, column: Callable[[T], TProp], instance: T) -> BaseCaster[TProp, Type[TProp]]: ...
    @overload
    def for_column[T, TProp](self, column: TProp, instance: T) -> BaseCaster[TProp, Type[TProp]]: ...

    def for_column[T, TProp: ColumnType](self, column: TProp | Callable[[T], TProp], instance: Optional[T]) -> BaseCaster[TProp]:
        if not instance:
            raise ValueError("You must specified an instance variable on the constructor before calling 'for_column' method")

        if GlobalChecker.is_lambda_function(column):
            column_type = column(type(instance)).dtype
            value = column(instance)
        else:
            column_type = column.dtype
            value = instance[column]

        return self._caster.cast(value, column_type)

    @overload
    def for_value[TProp](self, value: TProp) -> BaseCaster[TProp, Type[TProp]]: ...
    @overload
    def for_value[TProp, TType](self, value: TProp, value_type: TType) -> BaseCaster[TProp, TType]: ...

    def for_value[TProp, TType](self, value: TProp, value_type: Optional[TType] = None) -> BaseCaster[TProp, TType]:
        column_type = value_type if value_type else type(value)
        return self._caster.cast(value, column_type)
