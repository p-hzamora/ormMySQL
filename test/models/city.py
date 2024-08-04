from typing import Self
from orm import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)

from datetime import datetime

from orm.common.interfaces import IRepositoryBase
from .country import Country


class City(Table):
    __table_name__ = "city"

    city_id: int = Column[int](is_primary_key=True)
    city: str
    country_id: int
    last_update: datetime

    Country = ForeignKey[Self, Country](__table_name__, Country, lambda ci, co: ci.country_id == co.country_id)


class CityModel(BaseModel[City]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, City, repository)
