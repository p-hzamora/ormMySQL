from shapely import Point
from ormlambda import Column, Table

from datetime import datetime


class TableType(Table):
    __table_name__ = "table_type"

    pk: int = Column(int, is_primary_key=True, is_auto_increment=False)
    strings: str
    integers: int
    floats: float
    points: Point
    datetimes: datetime
