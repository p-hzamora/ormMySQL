from __future__ import annotations


from typing import ClassVar, Optional, Type, TYPE_CHECKING, Callable, overload, get_args
from types import NoneType
from ormlambda.caster.interfaces import ICaster
from ormlambda.common.global_checker import GlobalChecker
from ormlambda.sql.types import ColumnType
from ormlambda.caster import BaseCaster
from ormlambda.sql.sqltypes import TypeEngine


if TYPE_CHECKING:
    from ormlambda.caster import BaseCaster


class Caster(ICaster):
    PLACEHOLDER: ClassVar[str] = "%s"

    @classmethod
    def set_placeholder(cls, char: str) -> None:
        cls.PLACEHOLDER = char
        return None

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

        return self.cast(value, column_type)

    @overload
    def for_value[TProp](self, value: TProp) -> BaseCaster[TProp, Type[TProp]]: ...
    @overload
    def for_value[TProp, TType](self, value: TProp, value_type: TType) -> BaseCaster[TProp, TType]: ...

    def for_value[TProp, TType](self, value: TProp, value_type: Optional[TType] = None) -> BaseCaster[TProp, TType]:
        column_type = value_type if value_type else type(value)
        return self.cast(value, column_type)

    @classmethod
    def cast[TProp, TType](cls, value: TProp, type_value: Optional[TypeEngine[TType]] = None) -> BaseCaster[TProp, TType]:
        if len(args := get_args(type_value)) > 1:
            args = [x for x in args if x != NoneType]

            type_value = args[0]

        if isinstance(type_value, TypeEngine):
            column_type = type_value.python_type
        elif not type_value:
            column_type = type(value)
        else:
            column_type = type_value
        return cls.CASTER_SELECTOR()[column_type](value, column_type)
