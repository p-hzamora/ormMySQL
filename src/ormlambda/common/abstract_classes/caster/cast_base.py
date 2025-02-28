from __future__ import annotations
from datetime import datetime
from types import NoneType
import typing as tp
import abc
from shapely import Point
from ormlambda import Column

if tp.TYPE_CHECKING:
    from ormlambda.types import ColumnType


class CastBase(abc.ABC):
    @abc.abstractmethod
    def cast_str(value: ColumnType[str], insert_data: bool = False): ...
    @abc.abstractmethod
    def cast_int(value: ColumnType[int], insert_data: bool = False): ...
    @abc.abstractmethod
    def cast_float(value: ColumnType[float], insert_data: bool = False): ...
    @abc.abstractmethod
    def cast_Point(value: ColumnType[Point], insert_data: bool = False): ...
    @abc.abstractmethod
    def cast_NoneType(value: ColumnType[NoneType], insert_data: bool = False): ...
    @abc.abstractmethod
    def cast_datetime(value: ColumnType[datetime], insert_data: bool = False): ...

    @abc.abstractmethod
    def resolve[TProp](self, type_value: Column[TProp], value: ColumnType[TProp]) -> TProp: ...


class WriteCastBase(CastBase):
    def __init__(self) -> NoneType:
        self.SELECTOR: dict[tp.Type, tp.Callable[[tp.Any, tp.Optional[bool]], str]] = {
            str: self.cast_str,
            int: self.cast_int,
            float: self.cast_float,
            Point: self.cast_Point,
            NoneType: self.cast_NoneType,
            datetime: self.cast_datetime,
        }

    def resolve[TProp](self, type_value, value: ColumnType[TProp], insert_data: bool = False) -> TProp:
        if isinstance(value, Column):
            return value.column_name

        return self.SELECTOR.get(type_value, lambda c,_: str(c))(value, insert_data)


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

    def resolve[TProp](self, type_value: Column[TProp], value: ColumnType[TProp]) -> TProp:
        if isinstance(value, Column):
            return value.column_name

        if type(value) in self.SELECTOR:
            return value

        return self.SELECTOR.get(type_value, lambda c: str(c))(value)
