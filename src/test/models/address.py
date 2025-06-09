from datetime import datetime

from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)
from ormlambda.repository import IRepositoryBase
from .city import City
from ormlambda.sql.sqltypes import VARCHAR, INT, DATETIME, LargeBinary


class Address(Table):
    __table_name__ = "address"

    address_id: Column[int] = Column(INT(),check_types=False, is_primary_key=True)
    address: Column[str] = Column(VARCHAR(255),check_types=False)
    address2: Column[str] = Column(VARCHAR(255),check_types=False)
    district: Column[str] = Column(VARCHAR(255),check_types=False)
    city_id: Column[int] = Column(INT(),check_types=False)
    postal_code: Column[str] = Column(VARCHAR(255),check_types=False)
    phone: Column[str] = Column(VARCHAR(255),check_types=False)
    location: Column[bytes] = Column(LargeBinary(),check_types=False)
    last_update: Column[datetime] = Column(DATETIME(),check_types=False)

    City = ForeignKey["Address", City](City, lambda a, c: a.city_id == c.city_id)


class AddressModel(BaseModel[Address]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, Address, repository)
