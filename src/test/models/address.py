from datetime import datetime

from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)
from ormlambda import IRepositoryBase
from .city import City


class Address(Table):
    __table_name__ = "address"

    address_id: int = Column[int](is_primary_key=True)
    address: str
    address2: str
    district: str
    city_id: int
    postal_code: str
    phone: str
    location: str
    last_update: datetime = Column[datetime](is_auto_generated=True)

    City = ForeignKey["Address", City](__table_name__, City, lambda a, c: a.city_id == c.city_id)


class AddressModel(BaseModel[Address]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Address, repository)
