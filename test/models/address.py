from typing import NamedTuple, Optional
from datetime import datetime

from orm import (
    Column,
    Table,
    nameof,
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

    def __init__(
        self,
        address_id: int,
        address: Optional[str],
        address2: Optional[str],
        district: str,
        city_id: int,
        postal_code: str,
        phone: str,
        location: Point,
        last_update: datetime,
    ) -> None:
        self._address_id: Column[int] = Column(nameof(address_id), address_id, is_primary_key=True)
        self._address: Column[str] = Column(nameof(address), address)
        self._address2: Column[str] = Column(nameof(address2), address2)
        self._district: Column[str] = Column(nameof(district), district)
        self._city_id: Column[datetime] = Column(nameof(city_id), city_id)
        self._postal_code: Column[datetime] = Column(nameof(postal_code), postal_code)
        self._phone: Column[datetime] = Column(nameof(phone), phone)
        self._location: Column[datetime] = Column(nameof(location), location)
        self._last_update: Column[datetime] = Column(nameof(last_update), last_update)

        self.city: City = ForeignKey[Address, City](Address, City, lambda a, c: a.city_id == c.city_id)

    @property
    def address_id(self) -> int:
        return self._address_id.column_value

    @address_id.setter
    def address_id(self, value: int) -> None:
        self._address_id.column_value = value

    @property
    def address(self) -> Optional[str]:
        return self._address.column_value

    @address.setter
    def address(self, value: Optional[str]) -> None:
        self._address.column_value = value

    @property
    def address2(self) -> Optional[str]:
        return self._address2.column_value

    @address2.setter
    def address2(self, value: Optional[str]) -> None:
        self._address2.column_value = value

    @property
    def district(self) -> str:
        return self._district.column_value

    @district.setter
    def district(self, value: str) -> None:
        self._district.column_value = value

    @property
    def city_id(self) -> int:
        return self._city_id.column_value

    @city_id.setter
    def city_id(self, value: int) -> None:
        self._city_id.column_value = value

    @property
    def postal_code(self) -> str:
        return self._postal_code.column_value

    @postal_code.setter
    def postal_code(self, value: str):
        self._postal_code.column_value = value

    @property
    def phone(self) -> str:
        return self._phone.column_value

    @phone.setter
    def phone(self, value: str):
        self._phone.column_value = value

    @property
    def location(self) -> Point:
        return self._location.column_value

    @location.setter
    def location(self, value: Point):
        self._location.column_value = value

    @property
    def last_update(self) -> datetime:
        return self._last_update.column_value

    @last_update.setter
    def last_update(self, value: datetime):
        self._last_update.column_value = value


class AddressModel(ModelBase[Address]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Address, repository=repository)
