from datetime import datetime
from typing import Optional
from shapely import Point
from types import NoneType
from ormlambda.common.abstract_classes.caster.cast_base import ReadCastBase


from .types.datetime import MySQLReadDatetime
from .types.string import MySQLReadString
from .types.int import MySQLReadInt
from .types.float import MySQLReadFloat
from .types.point import MySQLReadPoint
from .types.none import MySQLReadNoneType


class MySQLReadCastBase(ReadCastBase):
    @staticmethod
    def cast_str(value: str) -> str:
        return MySQLReadString.cast(value)

    @staticmethod
    def cast_int(value: str) -> int:
        return MySQLReadInt.cast(value)

    @staticmethod
    def cast_float(value: str) -> float:
        return MySQLReadFloat.cast(value)

    @staticmethod
    def cast_Point(value: str) -> Point:
        return MySQLReadPoint.cast(value)

    @staticmethod
    def cast_NoneType(value: str) -> NoneType:
        return MySQLReadNoneType.cast(value)

    @staticmethod
    def cast_datetime(value: str) -> datetime:
        return MySQLReadDatetime.cast(value)
