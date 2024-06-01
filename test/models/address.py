from typing import NamedTuple
from datetime import datetime

from orm import (
    Column,
    Table,
    ModelBase,
    IRepositoryBase,
    ForeignKey,
)

from .city import City


class Point(NamedTuple):
    x: float
    y: float


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



class AddressModel(ModelBase[Address]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Address, repository=repository)
