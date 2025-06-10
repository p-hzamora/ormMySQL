from ormlambda import (
    Column,
    Table,
    BaseModel,
)

from datetime import datetime
from ormlambda.repository import IRepositoryBase
from ormlambda.sql.sqltypes import VARCHAR, INT, DATETIME


class Country(Table):
    __table_name__ = "country"

    country_id: Column[int] = Column(INT(), is_primary_key=True, check_types=False)
    country: Column[str] = Column(VARCHAR(50), check_types=False)
    last_update: Column[datetime] = Column(DATETIME(), check_types=False)


class CountryModel(BaseModel[Country]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, Country, repository)
