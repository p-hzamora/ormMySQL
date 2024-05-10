from orm import (
    Column,
    Table,
    nameof,
    ModelBase,
    IRepositoryBase,
)

from datetime import datetime


class Country(Table):
    __table_name__ = "country"

    def __init__(self, country_id: int, country: str, last_update: datetime) -> None:
        self._country_id: Column[int] = Column(
            nameof(country_id),
            country_id,
            is_primary_key=True,
        )
        self._country: Column[str] = Column(nameof(country), country)
        self._last_update: Column[datetime] = Column(nameof(last_update), last_update)

    @property
    def country_id(self) -> int:
        return self._country_id.column_value

    @country_id.setter
    def country_id(self, value: int) -> None:
        self._country_id.column_value = value

    @property
    def country(self) -> str:
        return self._country.column_value

    @country.setter
    def country(self, value: str) -> None:
        self._country.column_value = value

    @property
    def last_update(self) -> str:
        return self._last_update.column_value

    @last_update.setter
    def last_update(self, value: str) -> None:
        self._last_update.column_value = value


class CountryModel(ModelBase[Country]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Country, repository=repository)
