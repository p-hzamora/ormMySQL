from __future__ import annotations
import abc
from typing import overload, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ormlambda.caster import BaseCaster
    from shapely import Point
    from types import NoneType
    from datetime import datetime


type ValidTypes = Type[str] | Type[int] | Type[float] | Type[Point] | Type[NoneType] | Type[datetime]


class ICaster(abc.ABC):
    @abc.abstractmethod
    @overload
    @classmethod
    def cast[TProp](cls, value: TProp) -> BaseCaster[TProp, Type[TProp]]: ...
    @overload
    @classmethod
    def cast[TProp, TType](cls, value: TProp, type_value: TType) -> BaseCaster[TProp, TType]: ...

    @classmethod
    @abc.abstractmethod
    def CASTER_SELECTOR(cls) -> dict[ValidTypes, Type[BaseCaster]]: ...
