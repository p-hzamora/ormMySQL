from datetime import datetime

from src.ormmysql import (
    Column,
    Table,
    BaseModel,
    IRepositoryBase,
    ForeignKey,
)


class Country(Table):
    __table_name__ = "country"

    country_id: int = Column[int](is_primary_key=True)
    country: str
    last_update: datetime


class CountryModel(BaseModel[Country]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Country, repository=repository)


class City(Table):
    __table_name__ = "city"

    city_id: int = Column[int](is_primary_key=True)
    city: str
    country_id: int
    last_update: datetime

    country = ForeignKey["City", Country](__table_name__, Country, lambda ci, co: ci.country_id == co.country_id)


class CityModel(BaseModel[City]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(City, repository=repository)


class Address(Table):
    __table_name__ = "address"

    address_id: int = Column[int](is_primary_key=True)
    address: str
    address2: str
    district: str
    city_id: int
    postal_code: datetime
    phone: str
    location: datetime
    last_update: datetime = Column[datetime](is_auto_generated=True)

    city = ForeignKey["Address", City](__table_name__, City, lambda a, c: a.city_id == c.city_id)


class AddressModel(BaseModel[Address]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Address, repository=repository)
