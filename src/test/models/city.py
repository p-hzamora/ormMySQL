from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)

from datetime import datetime

from ormlambda.repository import IRepositoryBase
from .country import Country


class City(Table):
    __table_name__ = "city"

    city_id: Column[int] = Column(int, is_primary_key=True)
    city: Column[str]
    country_id: Column[int]
    last_update: Column[datetime]

    Country = ForeignKey["City", Country](Country, lambda ci, co: ci.country_id == co.country_id)


class CityModel(BaseModel[City]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, City, repository)
