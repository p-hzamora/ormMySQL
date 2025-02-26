from datetime import datetime
from shapely import Point
from types import NoneType
from ormlambda.common.abstract_classes.resolver import WriteCastBase

from .types.datetime import MySQLWriteDatetime
from .types.string import MySQLCastString
from .types.int import MySQLCastInt
from .types.float import MySQLCastFloat
from .types.point import MySQLCastPoint
from .types.none import MySQLCastNoneType


class MySQLWriteCastBase(WriteCastBase):
    @staticmethod
    def cast_str(value: str) -> str:
        return MySQLCastString.cast(value)

    @staticmethod
    def cast_int(value: int) -> str:
        return MySQLCastInt.cast(value)

    @staticmethod
    def cast_float(value: float) -> str:
        return MySQLCastFloat.cast(value)

    @staticmethod
    def cast_Point(value: Point) -> str:
        return MySQLCastPoint.cast(value)

    @staticmethod
    def cast_NoneType(value: NoneType) -> str:
        return MySQLCastNoneType.cast(value)

    @staticmethod
    def cast_datetime(value: datetime) -> str:
        return MySQLWriteDatetime.cast(value)
