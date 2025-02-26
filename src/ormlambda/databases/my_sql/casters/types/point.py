from shapely import Point
from .base_write import IWrite
from .base_read import IRead
import shapely.wkt as wkt


class MySQLCastPoint(IWrite[Point]):
    @staticmethod
    def cast(value: Point):
        """
        value has to be on wkt like 'POINT(5 -5)'
        """
        return f"ST_GeomFromText('{value.wkt}')"


class MySQLReadPoint(IRead[Point]):
    @staticmethod
    def cast(value: str) -> Point:
        return wkt.loads(value)
