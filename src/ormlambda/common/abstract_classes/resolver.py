from __future__ import annotations
from datetime import datetime
from types import NoneType
import typing as tp
import abc
from shapely import Point
from ormlambda import Column

from ormlambda.types import ColumnType


class CastBase(abc.ABC):
    PLACEHOLDER: str = "%s"

    @abc.abstractmethod
    def cast_str(value: ColumnType[str]): ...
    @abc.abstractmethod
    def cast_int(value: ColumnType[int]): ...
    @abc.abstractmethod
    def cast_float(value: ColumnType[float]): ...
    @abc.abstractmethod
    def cast_Point(value: ColumnType[Point]): ...
    @abc.abstractmethod
    def cast_NoneType(value: ColumnType[NoneType]): ...
    @abc.abstractmethod
    def cast_datetime(value: ColumnType[datetime]): ...

    @abc.abstractmethod
    def resolve[TProp](self, value: ColumnType[TProp]) -> TProp: ...


class WriteCastBase(CastBase):
    def __init__(self) -> NoneType:
        self.SELECTOR: dict[tp.Type, tp.Callable[[tp.Any], str]] = {
            str: self.cast_str,
            int: self.cast_int,
            float: self.cast_float,
            Point: self.cast_Point,
            NoneType: self.cast_NoneType,
            datetime: self.cast_datetime,
        }

    def resolve[TProp](self, value: ColumnType[TProp]) -> TProp:
        if isinstance(value, Column):
            return value.column_name
        return self.SELECTOR.get(type(value), lambda c: str(c))(value)


class ReadCastBase(CastBase):
    def __init__(self) -> NoneType:
        self.SELECTOR: dict[tp.Type, tp.Callable[[tp.Any], str]] = {
            str: self.cast_str,
            int: self.cast_int,
            float: self.cast_float,
            Point: self.cast_Point,
            NoneType: self.cast_NoneType,
            datetime: self.cast_datetime,
        }

    def resolve[TProp](self, value: ColumnType[TProp]) -> TProp:
        if isinstance(value, Column):
            return value.column_name
        return self.SELECTOR.get(type(value), lambda c: str(c))(value)
