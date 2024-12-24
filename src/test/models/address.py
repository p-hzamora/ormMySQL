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

    address_id: Column[int] = Column(int, is_primary_key=True)
    address: Column[str] = Column(str)
    address2: Column[str] = Column(str)
    district: Column[str] = Column(str)
    city_id: Column[int] = Column(int)
    postal_code: Column[str] = Column(str)
    phone: Column[str] = Column(str)
    location: Column[None | bytes] = Column(None | bytes)
    last_update: Column[datetime] = Column(datetime, is_auto_generated=True)

    City = ForeignKey["Address", City](City, lambda a, c: a.city_id == c.city_id)


class AddressModel(BaseModel[Address]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Address, repository)
