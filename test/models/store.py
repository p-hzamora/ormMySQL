from typing import Self
from orm import (
    Column,
    Table,
    ModelBase,
    IRepositoryBase,
    ForeignKey,
)

from datetime import datetime

from .address import Address

class Store(Table):
    __table_name__ = "store"

    store_id:int = Column[int](is_primary_key=True)
    manager_staff_id:int
    address_id:int
    last_update:datetime

    address = ForeignKey[Self, Address](__table_name__, Address, lambda s,a: s.store_id == a.address_id)


class StoreModel(ModelBase[Store]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Store, repository=repository)
