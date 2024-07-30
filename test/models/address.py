from datetime import datetime

from orm import (
    Column,
    Table,
    ModelBase,
    ForeignKey,
)
from orm.interfaces import IRepositoryBase
from orm.abstract_model import AbstractSQLStatements

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

    city = ForeignKey["Address", City](__table_name__, City, lambda a, c: a.city_id == c.city_id)


# FIXME [ ]: check to change initialization Model
class AddressModel(ModelBase[Address]):
    def __new__(cls, repository: IRepositoryBase) -> AbstractSQLStatements[Address]:
        return super().__new__(cls, Address, repository)
