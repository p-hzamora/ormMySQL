from ormlambda import (
    Column,
    Table,
    BaseModel,
)

from datetime import datetime
from ormlambda import IRepositoryBase


class Country(Table):
    __table_name__ = "country"

    country_id: Column[int] = Column(int, is_primary_key=True)
    country: Column[str]
    last_update: Column[datetime]


class CountryModel(BaseModel[Country]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Country, repository)
