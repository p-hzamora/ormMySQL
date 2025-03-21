from __future__ import annotations

from typing import Optional, get_args
from ormlambda.caster import BaseCaster
from ormlambda.caster import ICaster


from .types import StringCaster, IntegerCaster, FloatCaster, PointCaster, NoneTypeCaster, DatetimeCaster, BytesCaster, IterableCaster

from shapely import Point
from types import NoneType
from datetime import datetime


class MySQLCaster(ICaster):
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
            tuple: IterableCaster,
            list: IterableCaster,
        }

    @classmethod
    def cast[TProp, TType](cls, value: TProp, type_value: Optional[TType] = None) -> BaseCaster[TProp, TType]:
        if len(args := get_args(type_value)) > 1:
            args = [x for x in args if x != NoneType]

            type_value = args[0]

        column_type = type_value if type_value else type(value)
        return cls.CASTER_SELECTOR()[column_type](value, column_type)
