import shapely.wkt as wkt
from shapely import wkb
from shapely import Point

from ormlambda.caster import PLACEHOLDER
from .base_write import IWrite
from .base_read import IRead


class MySQLWritePoint(IWrite[Point]):
    @staticmethod
    def cast(value: str | Point, insert_data: bool = False) -> str:
        """
        value has to be on wkt like 'POINT(5 -5)'
        """
        if value == PLACEHOLDER:
            if insert_data:
                return f"ST_GeomFromText({value})"
        if isinstance(value, str):
            return f"ST_AsText({value})"

        if isinstance(value, Point):
            return value.wkt
        raise TypeError(f"Value '{type(value)}' unexpected.")


class MySQLReadPoint(IRead[Point]):
    @staticmethod
    def cast(value: str) -> Point:
        if isinstance(value, str):
            return wkt.loads(value)
        elif isinstance(value, bytes):
            return wkb.loads(value)
        raise TypeError(f"Value '{type(value)}' unexpected.")
