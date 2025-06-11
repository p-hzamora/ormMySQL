from __future__ import annotations
from ormlambda.caster.caster import Caster


from .types import (
    StringCaster,
    IntegerCaster,
    FloatCaster,
    PointCaster,
    NoneTypeCaster,
    DatetimeCaster,
    BytesCaster,
    IterableCaster,
    BooleanCaster,
)

from shapely import Point
from types import NoneType
from datetime import datetime


class MySQLCaster(Caster):
    PLACEHOLDER = "%s"

    @classmethod
    def CASTER_SELECTOR(cls):
        return {
            str: StringCaster,
            int: IntegerCaster,
            float: FloatCaster,
            Point: PointCaster,
            NoneType: NoneTypeCaster,
            datetime: DatetimeCaster,
            bytes: BytesCaster,
            bytearray: BytesCaster,
            tuple: IterableCaster,
            list: IterableCaster,
            bool: BooleanCaster,
        }
