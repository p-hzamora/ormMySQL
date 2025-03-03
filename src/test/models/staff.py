from typing import Self
from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)

from datetime import datetime

from ormlambda.repository import IRepositoryBase
from .address import Address
from .store import Store


class Staff(Table):
    __table_name__ = "staff"

    staff_id: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    first_name: Column[str] = Column(str)
    last_name: Column[str] = Column(str)
    address_id: Column[int] = Column(int)
    picture: Column[bytes] = Column(bytes)
    email: Column[str] = Column(str)
    store_id: Column[int] = Column(int)
    active: Column[int] = Column(int)
    username: Column[str] = Column(str)
    password: Column[str] = Column(str)
    last_update: Column[datetime] = Column(datetime)

    Address = ForeignKey[Self, Address](Address, lambda s, a: s.staff_id == a.address_id)
    Store = ForeignKey[Self, Store](Store, lambda staff, store: staff.staff_id == store.store_id)


class StaffModel(BaseModel[Staff]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, Staff, repository)
