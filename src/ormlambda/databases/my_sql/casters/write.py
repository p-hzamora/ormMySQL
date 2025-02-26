from datetime import datetime
from shapely import Point
from types import NoneType
from ormlambda.common.abstract_classes.resolver import WriteCastBase

from .types.datetime import MySQLWriteDatetime
from .types.string import MySQLWriteString
from .types.int import MySQLWriteInt
from .types.float import MySQLWriteFloat
from .types.point import MySQLWritePoint
from .types.none import MySQLWriteNoneType


class MySQLWriteCastBase(WriteCastBase):
    @staticmethod
    def cast_str(value: str) -> str:
        return MySQLWriteString.cast(value)

    @staticmethod
    def cast_int(value: int) -> str:
        return MySQLWriteInt.cast(value)

    @staticmethod
    def cast_float(value: float) -> str:
        return MySQLWriteFloat.cast(value)

    @staticmethod
    def cast_Point(value: Point) -> str:
        return MySQLWritePoint.cast(value)

    @staticmethod
    def cast_NoneType(value: NoneType) -> str:
        return MySQLWriteNoneType.cast(value)

    @staticmethod
    def cast_datetime(value: datetime) -> str:
        return MySQLWriteDatetime.cast(value)
