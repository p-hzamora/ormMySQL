from datetime import datetime
from shapely import Point
from types import NoneType
from ormlambda.common.abstract_classes.caster.cast_base import WriteCastBase

from .types.datetime import MySQLWriteDatetime
from .types.string import MySQLWriteString
from .types.int import MySQLWriteInt
from .types.float import MySQLWriteFloat
from .types.point import MySQLWritePoint
from .types.none import MySQLWriteNoneType


class MySQLWriteCastBase(WriteCastBase):
    @staticmethod
    def cast_str(value: str, insert_data: bool = False) -> str:
        return MySQLWriteString.cast(value, insert_data)

    @staticmethod
    def cast_int(value: int, insert_data: bool = False) -> str:
        return MySQLWriteInt.cast(value, insert_data)

    @staticmethod
    def cast_float(value: float, insert_data: bool = False) -> str:
        return MySQLWriteFloat.cast(value, insert_data)

    @staticmethod
    def cast_Point(value: Point, insert_data: bool = False) -> str:
        return MySQLWritePoint.cast(value, insert_data)

    @staticmethod
    def cast_NoneType(value: NoneType, insert_data: bool = False) -> str:
        return MySQLWriteNoneType.cast(value, insert_data)

    @staticmethod
    def cast_datetime(value: datetime, insert_data: bool = False) -> str:
        return MySQLWriteDatetime.cast(value, insert_data)
