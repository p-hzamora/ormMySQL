from orm import (
    Column,
    Table,
    nameof,
    ModelBase,
    IRepositoryBase,
    ForeignKey,
)

from datetime import datetime

from .country import Country


class City(Table):
    __table_name__ = "city"

    def __init__(
        self,
        city: str,
        country_id: int,
        city_id: int = None,
        last_update: datetime = None,
    ) -> None:
        self._city_id: Column[int] = Column(nameof(city_id), city_id, is_primary_key=True)
        self._city: Column[str] = Column(nameof(city), city)
        self._country_id: Column[str] = Column(nameof(country_id), country_id)
        self._last_update: Column[datetime] = Column(nameof(last_update), last_update)

        self.country: ForeignKey[City,Country] = ForeignKey[City,Country](
            orig_table=City,
            referenced_table=Country,
            relationship= lambda ci,co: ci.country_id == co.country_id
        )

    @property
    def city_id(self) -> int:
        return self._city_id.column_value

    @city_id.setter
    def city_id(self, value: int) -> None:
        self._city_id.column_value = value

    @property
    def city(self) -> str:
        return self._city.column_value

    @city.setter
    def city(self, value: str) -> None:
        self._city.column_value = value

    @property
    def country_id(self) -> int:
        return self._country_id.column_value

    @country_id.setter
    def country_id(self, value: int) -> None:
        self._country_id.column_value = value

    @property
    def last_update(self) -> str:
        return self._last_update.column_value

    @last_update.setter
    def last_update(self, value: str) -> None:
        self._last_update.column_value = value


class CityModel(ModelBase[City]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(City, repository=repository)
