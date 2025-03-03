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


class Store(Table):
    __table_name__ = "store"

    store_id: int = Column(int, is_primary_key=True)
    manager_staff_id: int
    address_id: int
    last_update: datetime

    Address = ForeignKey[Self, Address](Address, lambda s, a: s.store_id == a.address_id)


class StoreModel(BaseModel[Store]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, Store, repository)
