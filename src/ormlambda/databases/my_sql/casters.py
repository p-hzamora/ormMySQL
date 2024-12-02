from datetime import datetime
from shapely import Point
from types import NoneType
from ormlambda.utils.resolver import WriteCastBase, ReadCastBase
from shapely.wkt import loads

class MySQLReadCastBase(ReadCastBase):
    def cast_str(self, value: str) -> str:
        return str(value)

    def cast_int(self, value: str) -> int:
        return int(value)

    def cast_float(self, value: str) -> float:
        return float(value)

    def cast_Point(self, value: str) -> Point:
        """
        value has to be on wkt like 'POINT(5 -5)'
        """
        return loads(value)

    def cast_NoneType(self, value: str) -> NoneType:
        return None

    def cast_datetime(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


class MySQLWriteCastBase(WriteCastBase):
    def cast_str(self, value: str):
        return f"'{value}'"

    def cast_int(self, value: int):
        return str(value)

    def cast_float(self, value: float):
        return self.cast_int(value)

    def cast_Point(self, value: Point):
        return f"ST_GeomFromText('{value.wkt}')"

    def cast_NoneType(self, value: NoneType):
        return "NULL"

    def cast_datetime(self, value: datetime):
        return self.cast_str(value.strftime("%Y-%m-%d %H:%M:%S"))
    
# class MySQLComparisonBase(ComparisonBase): ...


