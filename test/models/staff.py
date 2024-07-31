from typing import Self
from orm import (
    Column,
    Table,
    ModelBase,
    ForeignKey,
)

from datetime import datetime

from orm.common.interfaces import IRepositoryBase
from orm.abstract_model import AbstractSQLStatements


from .address import Address
from .store import Store


class Staff(Table):
    __table_name__ = "staff"

    staff_id: int = Column[int](is_primary_key=True, is_auto_increment=True)
    first_name: str
    last_name: str
    address_id: str
    picture: bytes
    email: str
    store_id: int
    active: int
    username: str
    password: str
    last_update: datetime

    Address = ForeignKey[Self, Address](__table_name__, Address, lambda s, a: s.staff_id == a.address_id)
    Store = ForeignKey[Self, Store](__table_name__, Store, lambda staff, store: staff.staff_id == store.store_id)


# FIXME [ ]: check to change initialization Model
class StaffModel(ModelBase[Staff]):
    def __new__[T](cls, repository: T) -> AbstractSQLStatements[Staff,T]:
        return super().__new__(cls, Staff, repository=repository)