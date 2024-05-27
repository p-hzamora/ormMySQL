from orm import (
    Column,
    Table,
    ModelBase,
    IRepositoryBase,
)

from datetime import datetime


class Country(Table):
    __table_name__ = "country"

    country_id: int = Column[int](is_primary_key=True)
    country: str = Column[str]()
    last_update: datetime = Column[datetime]()


class CountryModel(ModelBase[Country]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Country, repository=repository)
