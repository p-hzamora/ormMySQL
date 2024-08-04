from orm import (
    Column,
    Table,
    ModelBase,
)

from datetime import datetime
from orm.common.interfaces import IRepositoryBase


class Country(Table):
    __table_name__ = "country"

    country_id: int = Column[int](is_primary_key=True)
    country: str
    last_update: datetime


class CountryModel(ModelBase[Country]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Country, repository)
