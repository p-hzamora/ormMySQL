from datetime import datetime

from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)
from ormlambda.repository import IRepositoryBase
from .city import City


class Address(Table):
    __table_name__ = "address"

    address_id: Column[int] = Column(int, is_primary_key=True)
    address: Column[str]
    address2: Column[str]
    district: Column[str]
    city_id: Column[int]
    postal_code: Column[str]
    phone: Column[str]
    location: Column[bytes]
    last_update: Column[datetime] = Column(datetime, is_auto_generated=True)

    City = ForeignKey["Address", City](City, lambda a, c: a.city_id == c.city_id)


class AddressModel(BaseModel[Address]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, Address, repository)
