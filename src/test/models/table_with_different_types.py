from shapely import Point
from ormlambda import (
    Column,
    Table,
    BaseModel,
)

from datetime import datetime

from ormlambda.repository import IRepositoryBase


class TableType(Table):
    __table_name__ = "table_type"

    pk: int = Column(int, is_primary_key=True, is_auto_increment=True)
    strings: str
    integers: int
    floats: float
    points: Point
    datetimes: datetime


class TableTypeModel(BaseModel[TableType]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, TableType, repository)
